import datetime
import aiohttp
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy import and_, delete, insert, select, update, func, case
from src.utils.jwt_utils import create_jwt
from src.commons.validator import (
    validate_conversation_data,
    validate_jwt_data,
    validate_profile_data,
    validate_signup_data,
    validate_forgot_pwd_data,
    validate_update_pwd_data,
    validate_signin_data,
    validate_otp_data,
)
from src.constants.constants import Constants
from src.constants.global_data import GlobalData
from src.utils.db_utils import db_connect
from src.utils.traceback_utils import print_traceback
from src.utils.web_socket_utils import manager
from src.commons.email_auth import pin_generator, send_email
from src.utils.encryption_utils import decrypt
from src.utils.pwd_utils import create_password
from src.utils.send_notifcation import send_device_notification

router = APIRouter()
from src.utils.logger import Logger

logger = Logger.get_logger()


@router.post("/user/get_direct_users")
async def get_direct_users(request: Request):
    """
    Return a list of direct (connected) users for the requester.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL (email of requester)

    Success: returns a JSON response containing the users list under
    `Constants.USERS_STRING` and a `Constants.SUCCESS_CODE` status.
    Errors: validates JWT and will return error messages/status codes
    from `GlobalData.STATUS_CODE` / `Constants.APPLICATION_ERROR_MESSAGE` on exception.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_jwt_data(input_params)

        requester_email = input_params[Constants.JWT_PARAM_EMAIL].lower()

        await db_connect.get_data(Constants.USER_TABLE, email=requester_email)

        users_dict = await db_connect.get_user_data(current_user_email=requester_email)
        print(users_dict)
        response[Constants.USERS_STRING] = users_dict
        response[Constants.MESSAGE_KEY] = Constants.SUCCESS_CODE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = GlobalData.STATUS_CODE
        response[Constants.MESSAGE_KEY] = Constants.APPLICATION_ERROR_MESSAGE
        GlobalData.STATUS_CODE = Constants.INTERNAL_SERVER

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/get_all_users")
async def get_all_users(request: Request):
    """
    Return all users in the system except the requester.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL (email of requester)

    Success: returns a JSON response containing all users under
    `Constants.USERS_STRING` with a success status code.
    Errors: will propagate validation errors or internal server errors.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_jwt_data(input_params)

        requester_email = input_params[Constants.JWT_PARAM_EMAIL].lower()

        await db_connect.get_data(Constants.USER_TABLE, email=requester_email)

        users_dict = await db_connect.get_all_user_data(exclude_email=requester_email)

        response[Constants.USERS_STRING] = users_dict
        response[Constants.MESSAGE_KEY] = Constants.SUCCESS_CODE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = GlobalData.STATUS_CODE
        response[Constants.MESSAGE_KEY] = Constants.APPLICATION_ERROR_MESSAGE
        GlobalData.STATUS_CODE = Constants.INTERNAL_SERVER

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/conversation_start")
async def start_conversation(request: Request):
    """
    Start a conversation. Supports group and private conversations.

    Expected request JSON keys (via Constants):
        - Constants.CREATED_BY_EMAIL (creator email)
        - Constants.PARTICIPANTS (list of participant emails)
        - Constants.CONVERSATION_NAME (optional)
        - Constants.CONVERSATION_TYPE (Constants.GROUP or Constants.PRIVATE)

    Success: creates conversation(s) and participants entries and returns
    created conversation ids under `Constants.CONVERSATION_ID` with a success code.
    Errors: validates input and returns appropriate error messages/status codes.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()

    try:
        input_params = await request.json()
        validate_conversation_data(input_params)

        creator_email = input_params.get(Constants.CREATED_BY_EMAIL, "").lower()
        participant_emails = [
            email.lower() for email in input_params.get(Constants.PARTICIPANTS, [])
        ]
        conversation_name = input_params.get(Constants.CONVERSATION_NAME, "")
        conversation_type = input_params.get(
            Constants.CONVERSATION_TYPE, Constants.CONVERSATION_TYPE_DIRECT
        )

        if not creator_email or not participant_emails:
            response[
                Constants.MESSAGE_KEY
            ] = Constants.MISSING_CONVERSATION_FIELDS_MESSAGE
            response[Constants.STATUS_CODE_KEY] = Constants.BAD_REQUEST
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        now = datetime.datetime.now().strftime(Constants.DATETIME_FORMAT)
        user_model = db_connect.models[Constants.USER_TABLE]

        async with db_connect.AsyncSessionLocal() as session:
            creator_uid = await session.scalar(
                select(user_model.uid).where(user_model.email == creator_email)
            )

            if not creator_uid:
                response[
                    Constants.MESSAGE_KEY
                ] = Constants.USER_NOT_FOUND_MESSAGE.format(creator_email)
                response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR
                return JSONResponse(
                    content=response, status_code=response[Constants.STATUS_CODE_KEY]
                )

            participant_uids = []
            for email in participant_emails:
                uid = await session.scalar(
                    select(user_model.uid).where(user_model.email == email)
                )
                if uid:
                    participant_uids.append(uid)

            if not participant_uids:
                response[
                    Constants.MESSAGE_KEY
                ] = Constants.CONVERSATION_PARTICIPANTS_ERROR
                response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR
                return JSONResponse(
                    content=response, status_code=response[Constants.STATUS_CODE_KEY]
                )

        conversation_model = db_connect.models[Constants.CONVERSATION_TABLE]
        participants_model = db_connect.models[
            Constants.CONVERSATION_PARTICIPANTS_TABLE
        ]

        created_conversation_ids = []

        async with db_connect.AsyncSessionLocal() as session:
            async with session.begin():
                if conversation_type == Constants.GROUP:
                    new_conversation = conversation_model(
                        conversation_name=conversation_name,
                        conversation_type=Constants.GROUP,
                        created_by=creator_uid,
                        created_on=now,
                    )
                    session.add(new_conversation)
                    await session.flush()

                    conversation_id = new_conversation.conversation_id
                    created_conversation_ids.append(conversation_id)

                    session.add_all(
                        [
                            participants_model(
                                conversation_id=conversation_id,
                                uid=creator_uid,
                                joined_on=now,
                                role=Constants.ADMIN,
                            ),
                            *[
                                participants_model(
                                    conversation_id=conversation_id,
                                    uid=uid,
                                    joined_on=now,
                                    role=Constants.MEMBER,
                                )
                                for uid in participant_uids
                            ],
                        ]
                    )

                else:
                    for uid in participant_uids:
                        new_conversation = conversation_model(
                            conversation_name=conversation_name,
                            conversation_type=Constants.PRIVATE,
                            created_by=creator_uid,
                            created_on=now,
                        )
                        session.add(new_conversation)
                        await session.flush()

                        conversation_id = new_conversation.conversation_id
                        created_conversation_ids.append(conversation_id)

                        session.add_all(
                            [
                                participants_model(
                                    conversation_id=conversation_id,
                                    uid=creator_uid,
                                    joined_on=now,
                                    role=Constants.ADMIN,
                                ),
                                participants_model(
                                    conversation_id=conversation_id,
                                    uid=uid,
                                    joined_on=now,
                                    role=Constants.MEMBER,
                                ),
                            ]
                        )

        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        response[Constants.MESSAGE_KEY] = Constants.CONVERSATION_SUCCESS_MESSAGE
        response[Constants.CONVERSATION_ID] = created_conversation_ids

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = Constants.CONVERSATION_ERROR_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/conversations")
async def get_user_conversations(request: Request):
    """
    Fetch conversations for a given user along with participants, last message and unread count.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL (email of requester)

    Success: returns a list under `Constants.CONVERSATIONS_STRING_LOWER` and a success status.
    Errors: returns user existence errors or internal server errors.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()

    try:
        input_params = await request.json()
        user_email = input_params.get(Constants.JWT_PARAM_EMAIL, "").lower()

        if not user_email:
            return JSONResponse(
                status_code=Constants.BAD_REQUEST,
                content={
                    Constants.STATUS_CODE_KEY: Constants.BAD_REQUEST,
                    Constants.MESSAGE_KEY: Constants.INVALID_REQUEST_PARAMETERS_MESSAGE,
                },
            )

        users_model = await db_connect.set_up_table(Constants.USER_TABLE)
        conv_model = await db_connect.set_up_table(Constants.CONVERSATION_TABLE)
        conv_participants_model = await db_connect.set_up_table(
            Constants.CONVERSATION_PARTICIPANTS_TABLE
        )
        msg_model = await db_connect.set_up_table(Constants.MESSAGE_TABLE)
        receipts_model = await db_connect.set_up_table(Constants.RECEIPTS_TABLE)
        cleared_model = await db_connect.set_up_table(
            Constants.CONVERSATION_CLEARED_TABLE
        )

        async with db_connect.AsyncSessionLocal() as session:
            uid = await session.scalar(
                select(users_model.uid).where(users_model.email == user_email)
            )
            if not uid:
                return JSONResponse(
                    status_code=Constants.USER_EXISTENCE_ERROR,
                    content={
                        Constants.STATUS_CODE_KEY: Constants.USER_EXISTENCE_ERROR,
                        Constants.MESSAGE_KEY: Constants.USER_EXISTENCE_ERROR_MESSAGE,
                    },
                )

            conv_query = (
                select(
                    conv_model.conversation_id,
                    conv_model.conversation_name,
                    conv_model.conversation_type,
                )
                .join(
                    conv_participants_model,
                    conv_model.conversation_id
                    == conv_participants_model.conversation_id,
                )
                .where(conv_participants_model.uid == uid)
            )

            conversations = (await session.execute(conv_query)).all()
            results = []

            for conv_id, name, conv_type in conversations:
                participants_query = (
                    select(
                        users_model.uid,
                        users_model.first_name,
                        users_model.last_name,
                        users_model.email,
                    )
                    .join(
                        conv_participants_model,
                        users_model.uid == conv_participants_model.uid,
                    )
                    .where(conv_participants_model.conversation_id == conv_id)
                )
                participant_rows = (await session.execute(participants_query)).all()
                participants = [
                    {
                        Constants.UID: p_uid,
                        Constants.FIRST_NAME: fn,
                        Constants.LAST_NAME: ln,
                        Constants.EMAIL: em,
                    }
                    for p_uid, fn, ln, em in participant_rows
                ]

                if (
                    conv_type == Constants.PRIVATE
                    and (not name or name.strip() == "")
                    and len(participants) == 2
                ):
                    sorted_names = sorted(
                        [
                            f"{p[Constants.FIRST_NAME]} {p[Constants.LAST_NAME]}".strip()
                            for p in participants
                        ]
                    )
                    name = f"{sorted_names[0]} & {sorted_names[1]}"

                cleared_at = await session.scalar(
                    select(cleared_model.cleared_at)
                    .where(cleared_model.uid == uid)
                    .where(cleared_model.conversation_id == conv_id)
                )

                last_msg_query = select(
                    msg_model.body, msg_model.sent_at, msg_model.uid
                ).where(msg_model.conversation_id == conv_id)
                if cleared_at:
                    last_msg_query = last_msg_query.where(
                        msg_model.sent_at > cleared_at
                    )
                last_msg_query = last_msg_query.order_by(
                    msg_model.sent_at.desc()
                ).limit(1)

                last_msg = (await session.execute(last_msg_query)).first()

                if last_msg:
                    last_message = {
                        Constants.TEXT: last_msg[0],
                        Constants.CREATED_AT: str(last_msg[1]),
                        Constants.SENT_BY_ME: last_msg[2] == uid,
                    }
                else:
                    last_message = None

                unread_query = (
                    select(receipts_model.message_id)
                    .join(msg_model, receipts_model.message_id == msg_model.message_id)
                    .where(msg_model.conversation_id == conv_id)
                    .where(receipts_model.uid == uid)
                    .where(receipts_model.status != Constants.READ)
                    .where(msg_model.uid != uid)
                )
                if cleared_at:
                    unread_query = unread_query.where(msg_model.sent_at > cleared_at)

                unread_count = len((await session.scalars(unread_query)).all())

                results.append(
                    {
                        Constants.CONVERSATION_ID: conv_id,
                        Constants.CONVERSATION_NAME: name,
                        Constants.CONVERSATION_TYPE: conv_type,
                        Constants.LAST_MESSAGE: last_message,
                        Constants.UNREAD_COUNT: unread_count,
                        Constants.PARTICIPANTS: participants,
                    }
                )

        return JSONResponse(
            status_code=Constants.SUCCESS_CODE,
            content={
                Constants.STATUS_CODE_KEY: Constants.SUCCESS_CODE,
                Constants.MESSAGE_KEY: Constants.CONVERSATION_FETCH_SUCCESS_MESSAGE,
                Constants.CONVERSATIONS_STRING_LOWER: results,
            },
        )

    except Exception as e:
        print_traceback(e)
        return JSONResponse(
            status_code=Constants.INTERNAL_SERVER,
            content={
                Constants.STATUS_CODE_KEY: Constants.INTERNAL_SERVER,
                Constants.MESSAGE_KEY: Constants.CONVERSATION_FETCH_ERROR_MESSAGE,
            },
        )


@router.websocket("/user/send_message_ws/{conversation_id}/{email}")
async def send_message_ws(websocket: WebSocket, conversation_id: int, email: str):
    """
    WebSocket endpoint for sending messages in a conversation.

    Path parameters:
        - conversation_id: integer conversation identifier
        - email: sender's email

    Message payload (JSON) should include:
        - Constants.BODY (message text)

    Behavior: saves message, creates delivery receipts, broadcasts to participants,
    sends push notifications to registered devices, and acknowledges to the sender.
    """

    await websocket.accept()
    sender_email = email.lower()

    logger.info(f"WebSocket CONNECT - convo={conversation_id}, user={sender_email}")
    await manager.connect(conversation_id, sender_email, websocket)

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except WebSocketDisconnect:
                logger.warning(
                    f"WebSocket DISCONNECTED - convo={conversation_id}, user={sender_email}"
                )
                break
            except Exception as e:
                logger.warning(f"WebSocket JSON error (ignored) - {e}")
                continue

            logger.debug(
                f"Received message from {sender_email} in convo={conversation_id}: {data}"
            )
            message_text = data.get(Constants.BODY, "")
            if not message_text:
                await websocket.send_json(
                    {
                        Constants.STATUS_CODE_KEY: Constants.BAD_REQUEST,
                        Constants.MESSAGE_KEY: Constants.MISSING_MESSAGE_FIELDS_MESSAGE,
                    }
                )
                logger.warning(f"Empty message received from {sender_email}")
                continue

            users_model = await db_connect.set_up_table(Constants.USER_TABLE)
            msg_model = await db_connect.set_up_table(Constants.MESSAGE_TABLE)
            receipt_model = await db_connect.set_up_table(Constants.RECEIPTS_TABLE)
            conv_part_model = await db_connect.set_up_table(
                Constants.CONVERSATION_PARTICIPANTS_TABLE
            )
            devices_model = await db_connect.set_up_table("devices")

            async with db_connect.AsyncSessionLocal() as session:
                sender_uid = await session.scalar(
                    select(users_model.uid).where(users_model.email == sender_email)
                )

                now = datetime.datetime.now().strftime(Constants.DATETIME_FORMAT)

                new_msg = msg_model(
                    conversation_id=conversation_id,
                    uid=sender_uid,
                    body=message_text,
                    sent_at=now,
                )
                session.add(new_msg)
                await session.flush()
                message_id = new_msg.message_id
                logger.info(
                    f"Message saved - id={message_id}, convo={conversation_id}, user={sender_email}"
                )

                participant_uids = (
                    await session.scalars(
                        select(conv_part_model.uid)
                        .where(conv_part_model.conversation_id == conversation_id)
                        .where(conv_part_model.uid != sender_uid)
                    )
                ).all()

                for uid in participant_uids:
                    session.add(
                        receipt_model(
                            message_id=message_id,
                            uid=uid,
                            status="delivered",
                            updated_at=now,
                        )
                    )

                await session.commit()

                sender_name = sender_email.split("@")[0].capitalize()
                try:
                    result = await session.execute(
                        select(users_model.first_name).where(
                            users_model.email == sender_email
                        )
                    )
                    sender_first_name = result.scalar_one_or_none()
                    if sender_first_name:
                        sender_name = sender_first_name
                    logger.info(f"Sender first name fetched: {sender_name}")
                except Exception as e:
                    logger.error(
                        f"Failed to fetch sender first name for {sender_email}: {e}"
                    )

                for uid in participant_uids:
                    device_ids = await session.scalars(
                        select(devices_model.device_id).where(devices_model.uid == uid)
                    )
                    for device_id in device_ids:
                        try:
                            await send_device_notification(
                                device_id,
                                title=f"New Message from {sender_name}",
                                body=message_text,
                            )
                            logger.info(
                                f"Notification sent to device={device_id} for user_uid={uid}"
                            )
                        except Exception as notify_err:
                            logger.error(
                                f"Failed to send notification to device={device_id}: {notify_err}"
                            )

            ack_message = {
                Constants.MESSAGE_ID: message_id,
                Constants.CONVERSATION_ID: conversation_id,
                Constants.TEXT: message_text,
                Constants.SENDER: sender_email,
                Constants.STATUS: Constants.SENT,
                Constants.SENT_AT: now,
            }
            await websocket.send_json(ack_message)
            logger.debug(f"Sent ack to sender {sender_email}: SENT")

            delivered_to_someone = await manager.broadcast(
                conversation_id,
                {
                    Constants.MESSAGE_ID: message_id,
                    Constants.CONVERSATION_ID: conversation_id,
                    Constants.TEXT: message_text,
                    Constants.SENDER: sender_email,
                    Constants.STATUS: Constants.DELIVERED,
                    Constants.SENT_AT: now,
                },
            )

            if delivered_to_someone:
                ack_message[Constants.STATUS] = Constants.DELIVERED
                await websocket.send_json(ack_message)
                logger.info(
                    f"Delivery confirmed to sender {sender_email} (status → delivered)"
                )
            else:
                logger.info(
                    f"No active receivers in convo={conversation_id}. "
                    f"Message stays SENT for sender {sender_email}."
                )

    except Exception as e:
        logger.exception(
            f"Unexpected error in WebSocket convo={conversation_id}, user={sender_email}"
        )
    finally:
        await manager.disconnect(conversation_id, sender_email)
        logger.info(f"WebSocket CLOSED - convo={conversation_id}, user={sender_email}")


@router.post("/user/get_messages")
async def get_messages(request: Request):
    """
    Retrieve messages for a conversation for the requesting user.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL (requester email)
        - Constants.MESSAGE_CONVERSATION_ID (conversation id)

    Success: returns messages list and message metadata; marks status fields as appropriate.
    Errors: returns bad request when parameters are missing or user is not participant.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        data = await request.json()
        reader_email = data.get(Constants.JWT_PARAM_EMAIL, "").lower()
        conversation_id = data.get(Constants.MESSAGE_CONVERSATION_ID)

        if not reader_email or not conversation_id:
            response[
                Constants.MESSAGE_KEY
            ] = Constants.INVALID_REQUEST_PARAMETERS_MESSAGE
            response[Constants.STATUS_CODE_KEY] = Constants.BAD_REQUEST
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        users_model = await db_connect.set_up_table(Constants.USER_TABLE)
        conv_part_model = await db_connect.set_up_table(
            Constants.CONVERSATION_PARTICIPANTS_TABLE
        )
        msg_model = await db_connect.set_up_table(Constants.MESSAGE_TABLE)
        receipts_model = await db_connect.set_up_table(Constants.RECEIPTS_TABLE)
        cleared_model = await db_connect.set_up_table(
            Constants.CONVERSATION_CLEARED_TABLE
        )

        async with db_connect.AsyncSessionLocal() as session:
            reader_uid = await session.scalar(
                select(users_model.uid).where(users_model.email == reader_email)
            )
            if not reader_uid:
                response[Constants.MESSAGE_KEY] = Constants.USER_EXISTENCE_ERROR_MESSAGE
                response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR
                return JSONResponse(
                    content=response, status_code=response[Constants.STATUS_CODE_KEY]
                )

            is_participant = await session.scalar(
                select(conv_part_model.uid)
                .where(conv_part_model.conversation_id == conversation_id)
                .where(conv_part_model.uid == reader_uid)
            )
            if not is_participant:
                response[Constants.MESSAGE_KEY] = Constants.USER_NOT_PART_OF_THIS_CONVO
                response[Constants.STATUS_CODE_KEY] = Constants.BAD_REQUEST
                return JSONResponse(
                    content=response, status_code=response[Constants.STATUS_CODE_KEY]
                )

            cleared_at = await session.scalar(
                select(cleared_model.cleared_at)
                .where(cleared_model.uid == reader_uid)
                .where(cleared_model.conversation_id == conversation_id)
            )

            query = (
                select(
                    msg_model.message_id,
                    msg_model.body,
                    msg_model.uid,
                    msg_model.sent_at,
                    users_model.email,
                    users_model.first_name,
                    receipts_model.status,
                )
                .join(users_model, users_model.uid == msg_model.uid)
                .outerjoin(
                    receipts_model,
                    and_(
                        receipts_model.message_id == msg_model.message_id,
                        receipts_model.uid == reader_uid,
                    ),
                )
                .where(msg_model.conversation_id == conversation_id)
                .order_by(msg_model.sent_at.asc())
            )
            if cleared_at:
                query = query.where(msg_model.sent_at > cleared_at)
                print(
                    f"[LOG] Messages cleared for user {reader_email} at {cleared_at} and model message {msg_model.sent_at}"
                )

            rows = (await session.execute(query)).all()

            messages_list = []
            for (
                m_id,
                body,
                sender_uid,
                sent_at,
                sender_email,
                sender_first_name,
                my_receipt_status,
            ) in rows:
                print(
                    f"[LOG] Message {m_id} sent at {sent_at}, cleared_at={cleared_at}"
                )
                sent_by_me = sender_uid == reader_uid

                if sent_by_me:
                    worst_status = await session.scalar(
                        select(receipts_model.status)
                        .where(receipts_model.message_id == m_id)
                        .order_by(
                            case(
                                (receipts_model.status == Constants.READ, 3),
                                (receipts_model.status == Constants.DELIVERED, 2),
                                else_=1,
                            )
                        )
                    )
                    status = worst_status if worst_status else Constants.SENT
                else:
                    status = (
                        my_receipt_status if my_receipt_status else Constants.DELIVERED
                    )

                sender_name = (
                    ""
                    if sent_by_me
                    else (
                        sender_first_name
                        if sender_first_name
                        else sender_email.split("@")[0].capitalize()
                    )
                )

                messages_list.append(
                    {
                        Constants.MESSAGE_ID: m_id,
                        Constants.CONVERSATION_ID: conversation_id,
                        Constants.TEXT: body,
                        Constants.SENDER: reader_email if sent_by_me else sender_email,
                        Constants.STATUS: status,
                        Constants.SENT_AT: str(sent_at),
                        Constants.SENT_BY_ME: bool(sent_by_me),
                        Constants.SENDER_NAME: sender_name,
                    }
                )
        print(
            f"[LOG] Returning {len(messages_list)} messages for user {reader_email} in conversation {conversation_id}"
        )
        response[Constants.MESSAGE_KEY] = Constants.MESSAGE_FETCH_SUCCESS_MESSAGE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        response[Constants.MESSAGE_KEY] = messages_list
    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = Constants.ERROR_FETCHING_MESSAGES

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/message_read")
async def mark_messages_read(request: Request):
    """
    Mark unread messages as read for the requesting user in a conversation.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL (reader email)
        - Constants.MESSAGE_CONVERSATION_ID (conversation id)

    Behavior: updates receipts to Constants.READ and broadcasts read receipts to other participants.
    Returns success or appropriate error messages.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()

    try:
        input_params = await request.json()
        reader_email = input_params.get(Constants.JWT_PARAM_EMAIL, "").lower()
        conversation_id = input_params.get(Constants.MESSAGE_CONVERSATION_ID)

        if not reader_email or not conversation_id:
            response[Constants.MESSAGE_KEY] = "email and conversation_id are required."
            response[Constants.STATUS_CODE_KEY] = Constants.BAD_REQUEST
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        users_model = await db_connect.set_up_table(Constants.USER_TABLE)
        msg_model = await db_connect.set_up_table(Constants.MESSAGE_TABLE)
        receipts_model = await db_connect.set_up_table(Constants.RECEIPTS_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            uid_row = await session.execute(
                select(users_model.uid).where(users_model.email == reader_email)
            )
            reader_uid = uid_row.scalar_one_or_none()

            if not reader_uid:
                response[Constants.MESSAGE_KEY] = f"User not found: {reader_email}"
                response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR
                return JSONResponse(
                    content=response, status_code=response[Constants.STATUS_CODE_KEY]
                )

            now = datetime.datetime.now().strftime(Constants.DATETIME_FORMAT)

            unread_messages_query = (
                select(
                    receipts_model.message_id,
                    msg_model.uid.label("sender_uid"),
                    users_model.email.label("sender_email"),
                )
                .join(msg_model, receipts_model.message_id == msg_model.message_id)
                .join(users_model, msg_model.uid == users_model.uid)
                .where(receipts_model.uid == reader_uid)
                .where(receipts_model.status != Constants.READ)
                .where(msg_model.conversation_id == conversation_id)
            )

            unread_messages = (await session.execute(unread_messages_query)).all()

        logger.info(
            f"[DEBUG] Marking {len(unread_messages)} messages as read for {reader_email}"
        )

        for msg_id, sender_uid, sender_email in unread_messages:
            await db_connect.update_data(
                Constants.RECEIPTS_TABLE,
                Constants.MESSAGE_ID,
                msg_id,
                status=Constants.READ,
                updated_at=now,
            )

            await manager.broadcast(
                conversation_id,
                {
                    Constants.MESSAGE_ID: msg_id,
                    Constants.CONVERSATION_ID: conversation_id,
                    Constants.STATUS: Constants.READ,
                },
                exclude_email=reader_email,
            )

            logger.debug(
                f"Broadcasted read status for message {msg_id} (from {sender_email})"
            )

        response[Constants.MESSAGE_KEY] = "Messages marked as read"
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = "Error updating message receipts"

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/clear_chat")
async def clear_chat(request: Request):
    """
    Clear a chat for a user by recording a cleared timestamp.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL (user email)
        - Constants.CONVERSATION_ID (conversation id)

    Behavior: updates or inserts a cleared timestamp for the user/conversation.
    Returns success or errors if user is not found.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()

        user_email = input_params.get(Constants.JWT_PARAM_EMAIL, "").lower()
        conversation_id = input_params.get(Constants.CONVERSATION_ID)

        if not user_email or not conversation_id:
            response[Constants.STATUS_CODE_KEY] = Constants.BAD_REQUEST
            response[
                Constants.MESSAGE_KEY
            ] = Constants.INVALID_REQUEST_PARAMETERS_MESSAGE
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        user = await db_connect.get_data(Constants.USER_TABLE, email=user_email)
        if not user:
            response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR
            response[Constants.MESSAGE_KEY] = Constants.USER_EXISTENCE_ERROR_MESSAGE
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        uid = user["uid"]

        ist = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

        cleared_at = datetime.datetime.now(ist)
        table_model = await db_connect.set_up_table(
            Constants.CONVERSATION_CLEARED_TABLE
        )

        async with db_connect.AsyncSessionLocal() as session:
            async with session.begin():
                stmt = (
                    update(table_model)
                    .where(table_model.uid == uid)
                    .where(table_model.conversation_id == conversation_id)
                    .values(cleared_at=cleared_at)
                )
                result = await session.execute(stmt)

                if result.rowcount == 0:
                    await session.execute(
                        table_model.__table__.insert().values(
                            uid=uid,
                            conversation_id=conversation_id,
                            cleared_at=cleared_at,
                        )
                    )
        print(
            f"[LOG] User {user_email} cleared chat for conversation {conversation_id} at {cleared_at}"
        )
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        response[Constants.MESSAGE_KEY] = Constants.CHAT_CLEARED_SUCCESS_MESSAGE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/otp_validate")
async def user_otp_validate(request: Request):
    """
    Validate OTP sent during forgot-password flow.

    Expected request JSON keys:
        - Constants.FORGOT_PASSWORD_PARAM_EMAIL (email)
        - Constants.OTP_VALIDATE_PARAM_OTP (otp value)

    Success: returns a success code when OTP matches; returns OTP mismatch error otherwise.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_otp_data(input_params)

        user_hashed_pin = create_password(
            str(input_params[Constants.OTP_VALIDATE_PARAM_OTP]),
            Constants.APP_SECRET_KEY,
        )

        user_existence = await db_connect.get_data(
            Constants.USER_TABLE,
            email=input_params[Constants.FORGOT_PASSWORD_PARAM_EMAIL].lower(),
            auth_info=user_hashed_pin,
        )

        if user_existence:
            response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
            response[Constants.MESSAGE_KEY] = Constants.SUCCESS_OTP_MATCH_MESSAGE
        else:
            response[Constants.STATUS_CODE_KEY] = Constants.OTP_MISMATCH_ERROR
            response[Constants.MESSAGE_KEY] = Constants.OTP_MISMATCH_ERROR_MESSAGE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/forgot-password")
async def user_forgot_pwd(request: Request):
    """
    Start forgot-password flow by generating an OTP and emailing it to the user.

    Expected request JSON keys:
        - Constants.FORGOT_PASSWORD_PARAM_EMAIL (email)

    Behavior: stores hashed OTP in user's auth_info and sends email with plain OTP.
    Returns success when email sent and user exists.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_forgot_pwd_data(input_params)

        user_existence = await db_connect.get_data(
            Constants.USER_TABLE,
            email=input_params[Constants.FORGOT_PASSWORD_PARAM_EMAIL].lower(),
        )

        if user_existence:
            otp_pin = pin_generator()
            hashed_pin = create_password(str(otp_pin), Constants.APP_SECRET_KEY)

            await db_connect.update_data(
                Constants.USER_TABLE,
                filter_field="email",
                filter_value=input_params[
                    Constants.FORGOT_PASSWORD_PARAM_EMAIL
                ].lower(),
                auth_info=hashed_pin,
            )

            send_email(input_params[Constants.FORGOT_PASSWORD_PARAM_EMAIL], otp_pin)

            response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
            response[Constants.MESSAGE_KEY] = Constants.SUCCESS_CODE_OTP_MESSAGE
        else:
            response[Constants.MESSAGE_KEY] = Constants.USER_EXISTENCE_ERROR_MESSAGE
            response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/reset-password")
async def user_reset_pwd(request: Request):
    """
    Reset user's password after OTP validation.

    Expected request JSON keys:
        - Constants.UPDATE_PASSWORD_PARAM_EMAIL (email)
        - Constants.UPDATE_PASSWORD_PARAM_PASSWORD (new password)

    Behavior: updates the stored password (hashed) and returns success.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_update_pwd_data(input_params)

        user_hashed_pwd = create_password(
            input_params[Constants.UPDATE_PASSWORD_PARAM_PASSWORD],
            Constants.APP_SECRET_KEY,
        )

        await db_connect.update_data(
            Constants.USER_TABLE,
            filter_field="email",
            filter_value=input_params[Constants.UPDATE_PASSWORD_PARAM_EMAIL].lower(),
            password=user_hashed_pwd,
        )

        response[Constants.MESSAGE_KEY] = Constants.SUCCESS_UPDATE_PASSWORD_MESSAGE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/signin")
async def user_signin(request: Request):
    """
    Authenticate a user with email and password.

    Expected request JSON keys:
        - Constants.SIGNIN_PARAM_EMAIL
        - Constants.SIGNIN_PARAM_PWD

    Success: returns success status and optional USER_NAME in response. On failure,
    returns credential or existence error codes.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_signin_data(input_params)

        user = await db_connect.get_data(
            Constants.USER_TABLE,
            email=input_params[Constants.SIGNIN_PARAM_EMAIL].lower(),
        )

        if user:
            user_hashed_pwd = create_password(
                input_params[Constants.SIGNIN_PARAM_PWD], Constants.APP_SECRET_KEY
            )

            if user_hashed_pwd == user["password"]:
                response[Constants.MESSAGE_KEY] = Constants.SIGNIN_SUCCESS_CODE_MESSAGE
                response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

                if user["first_name"] and user["last_name"]:
                    response[
                        Constants.USER_NAME_KEY
                    ] = f"{user['first_name']} {user['last_name']}"
                else:
                    response[Constants.USER_NAME_KEY] = (
                        user["first_name"] or user["email"]
                    )
            else:
                response[
                    Constants.MESSAGE_KEY
                ] = Constants.USER_CREDENTIAL_ERROR_MESSAGE
                response[Constants.STATUS_CODE_KEY] = Constants.USER_CREDENTIAL_ERROR
        else:
            response[Constants.MESSAGE_KEY] = Constants.USER_EXISTENCE_ERROR_MESSAGE
            response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/signup")
async def user_signup(request: Request):
    """
    Register a new user.

    Expected request JSON keys:
        - Constants.SIGNUP_PARAM_EMAIL
        - Constants.SIGNUP_PARAM_PWD

    Behavior: inserts a new user record with a hashed password and created_on timestamp.
    Returns success or user-exists error.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_signup_data(input_params)

        user = await db_connect.get_data(
            Constants.USER_TABLE,
            email=input_params[Constants.SIGNUP_PARAM_EMAIL].lower(),
        )

        if not user:
            hashed_pwd = create_password(
                input_params[Constants.SIGNUP_PARAM_PWD], Constants.APP_SECRET_KEY
            )

            time_now = datetime.datetime.now().strftime(Constants.DATETIME_FORMAT)

            await db_connect.insert_data(
                Constants.USER_TABLE,
                email=input_params[Constants.SIGNUP_PARAM_EMAIL].lower(),
                password=hashed_pwd,
                created_on=time_now,
            )

            response[Constants.MESSAGE_KEY] = Constants.SIGNUP_SUCCESS_CODE_MESSAGE
            response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        else:
            response[Constants.MESSAGE_KEY] = Constants.USER_ALREADY_EXISTS
            response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/profile")
async def user_profile(request: Request):
    """
    Update a user's profile fields (first_name, last_name, profile_image).

    Expected request JSON keys:
        - Constants.PROFILE_PARAM_EMAIL
        - Constants.PROFILE_PARAM_FIRST_NAME
        - Constants.PROFILE_PARAM_LAST_NAME
        - Constants.PROFILE_PARAM_IMAGE

    Returns success or an internal error on failure.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_profile_data(input_params)

        await db_connect.update_data(
            Constants.USER_TABLE,
            filter_field="email",
            filter_value=input_params[Constants.PROFILE_PARAM_EMAIL].lower(),
            first_name=input_params[Constants.PROFILE_PARAM_FIRST_NAME],
            last_name=input_params[Constants.PROFILE_PARAM_LAST_NAME],
            profile_image=input_params[Constants.PROFILE_PARAM_IMAGE],
        )

        response[Constants.MESSAGE_KEY] = Constants.SIGNUP_SUCCESS_CODE_MESSAGE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/generate_jwt")
async def generate_jwt(request: Request):
    """
    Generate a JWT token for the specified user email.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL

    Returns: JSON containing Constants.JWT_TOKEN on success.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_jwt_data(input_params)

        await db_connect.get_data(
            Constants.USER_TABLE, email=input_params[Constants.JWT_PARAM_EMAIL].lower()
        )

        user_jwt = create_jwt(
            user_email=input_params[Constants.JWT_PARAM_EMAIL].lower(),
            secret_key=decrypt(Constants.APP_SECRET_KEY),
        )

        response[Constants.MESSAGE_KEY] = Constants.JWT_SUCCESS_CODE_MESSAGE
        response[Constants.JWT_TOKEN] = user_jwt
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/fetch_profile")
async def fetch_profile(request: Request):
    """
    Fetch the profile information for the requested user (email, first/last name, profile image).

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL

    Returns: profile data under Constants.USERS_STRING on success; user existence errors otherwise.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()
        validate_jwt_data(input_params)

        user = await db_connect.get_data(
            Constants.USER_TABLE, email=input_params[Constants.JWT_PARAM_EMAIL].lower()
        )

        if user:
            profile_data = {
                Constants.PROFILE_PARAM_EMAIL: user["email"],
                Constants.PROFILE_PARAM_FIRST_NAME: user["first_name"],
                Constants.PROFILE_PARAM_LAST_NAME: user["last_name"],
                Constants.PROFILE_PARAM_IMAGE: user["profile_image"],
                Constants.CREATED_ON: str(user["created_on"]),
            }

            response[Constants.MESSAGE_KEY] = Constants.PROFILE_FETCH_SUCCESS_MESSAGE
            response[Constants.USERS_STRING] = profile_data
            response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        else:
            response[Constants.MESSAGE_KEY] = Constants.USER_EXISTENCE_ERROR_MESSAGE
            response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = Constants.PROFILE_FETCH_ERROR_MESSAGE

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/add_to_favorites")
async def add_to_favorites(request: Request):
    """
    Mark a conversation as favorite for the requesting user.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL
        - Constants.CONVERSATION_ID

    Returns success or error on failure.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()

        user = await db_connect.get_data(
            Constants.USER_TABLE, email=input_params[Constants.JWT_PARAM_EMAIL].lower()
        )
        user_id = user[Constants.UID]
        conv_id = input_params[Constants.CONVERSATION_ID]

        cp = await db_connect.set_up_table(Constants.CONVERSATION_PARTICIPANTS_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            async with session.begin():
                stmt = (
                    update(cp)
                    .where(cp.conversation_id == conv_id)
                    .where(cp.uid == user_id)
                    .values(is_favorite=Constants.YES)
                )
                await session.execute(stmt)

        response[Constants.MESSAGE_KEY] = Constants.ADD_TO_FAVORITES_SUCCESS_MESSAGE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        print(response)
        print(input_params)
    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(content=response)


@router.post("/user/remove_from_favorites")
async def remove_from_favorites(request: Request):
    """
    Remove a conversation from the requesting user's favorites.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL
        - Constants.CONVERSATION_ID

    Returns success or error on failure.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()

        user = await db_connect.get_data(
            Constants.USER_TABLE, email=input_params[Constants.JWT_PARAM_EMAIL].lower()
        )
        user_id = user[Constants.UID]
        conv_id = input_params[Constants.CONVERSATION_ID]

        cp = await db_connect.set_up_table(Constants.CONVERSATION_PARTICIPANTS_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            async with session.begin():
                stmt = (
                    update(cp)
                    .where(cp.conversation_id == conv_id)
                    .where(cp.uid == user_id)
                    .values(is_favorite=Constants.NO)
                )
                await session.execute(stmt)

        response[
            Constants.MESSAGE_KEY
        ] = Constants.REMOVE_FROM_FAVORITES_SUCCESS_MESSAGE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        print(response)
        print(input_params)
    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(content=response)


@router.post("/user/list_favorites")
async def list_favorites(request: Request):
    """
    List favorite conversations for the requesting user.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL

    Returns: list under Constants.FAVORITES_STRING_LOWER with conversation metadata.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()

        user = await db_connect.get_data(
            Constants.USER_TABLE, email=input_params[Constants.JWT_PARAM_EMAIL].lower()
        )
        user_id = user[Constants.UID]

        convo = await db_connect.set_up_table(Constants.CONVERSATION_TABLE)
        cp = await db_connect.set_up_table(Constants.CONVERSATION_PARTICIPANTS_TABLE)
        users_model = await db_connect.set_up_table(Constants.USER_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            query = (
                select(
                    convo.conversation_id,
                    convo.conversation_name,
                    convo.conversation_type,
                    cp.is_favorite,
                    cp.is_pinned,
                )
                .join(cp, cp.conversation_id == convo.conversation_id)
                .where(cp.uid == user_id)
                .where(cp.is_favorite == Constants.YES)
            )
            favorites = (await session.execute(query)).all()

            result_list = []
            for fav in favorites:
                participant_query = (
                    select(
                        func.concat(
                            users_model.first_name, " ", users_model.last_name
                        ).label("participant_name")
                    )
                    .select_from(cp)
                    .join(users_model, users_model.uid == cp.uid)
                    .where(cp.conversation_id == fav.conversation_id)
                    .where(cp.uid != user_id)
                )
                participant_res = await session.execute(participant_query)
                participant_name = participant_res.scalar() or ""

                result_list.append(
                    {
                        Constants.CONVERSATION_ID: fav.conversation_id,
                        Constants.CONVERSATION_NAME: fav.conversation_name,
                        Constants.CONVERSATION_TYPE: fav.conversation_type,
                        Constants.IS_FAVORITE: fav.is_favorite,
                        Constants.IS_PINNED: fav.is_pinned,
                        "participant_name": participant_name,
                    }
                )

        response[Constants.FAVORITES_STRING_LOWER] = result_list
        response[Constants.MESSAGE_KEY] = Constants.FAVORITES_FETCH_SUCCESS_MESSAGE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(content=response)


@router.post("/user/add_to_pinned")
async def add_to_pinned(request: Request):
    """
    Pin a conversation for the requesting user.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL
        - Constants.CONVERSATION_ID

    Returns success or error.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()

        user = await db_connect.get_data(
            Constants.USER_TABLE, email=input_params[Constants.JWT_PARAM_EMAIL].lower()
        )
        user_id = user[Constants.UID]
        conv_id = input_params[Constants.CONVERSATION_ID]

        cp = await db_connect.set_up_table(Constants.CONVERSATION_PARTICIPANTS_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            async with session.begin():
                stmt = (
                    update(cp)
                    .where(cp.conversation_id == conv_id)
                    .where(cp.uid == user_id)
                    .values(is_pinned=Constants.YES)
                )
                await session.execute(stmt)

        response[Constants.MESSAGE_KEY] = Constants.ADD_TO_PINNED_SUCCESS_MESSAGE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(content=response)


@router.post("/user/remove_from_pinned")
async def remove_from_pinned(request: Request):
    """
    Unpin a conversation for the requesting user.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL
        - Constants.CONVERSATION_ID

    Returns success or error.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()

        user = await db_connect.get_data(
            Constants.USER_TABLE, email=input_params[Constants.JWT_PARAM_EMAIL].lower()
        )
        user_id = user[Constants.UID]
        conv_id = input_params[Constants.CONVERSATION_ID]

        cp = await db_connect.set_up_table(Constants.CONVERSATION_PARTICIPANTS_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            async with session.begin():
                stmt = (
                    update(cp)
                    .where(cp.conversation_id == conv_id)
                    .where(cp.uid == user_id)
                    .values(is_pinned=Constants.NO)
                )
                await session.execute(stmt)

        response[Constants.MESSAGE_KEY] = "Removed from pinned successfully"
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(content=response)


@router.post("/user/list_pinned")
async def list_pinned(request: Request):
    """
    List pinned conversations for the requesting user.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL

    Returns: list under Constants.PINNED_STRING_LOWER.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()

        user = await db_connect.get_data(
            Constants.USER_TABLE, email=input_params[Constants.JWT_PARAM_EMAIL].lower()
        )
        user_id = user[Constants.UID]

        convo = await db_connect.set_up_table(Constants.CONVERSATION_TABLE)
        cp = await db_connect.set_up_table(Constants.CONVERSATION_PARTICIPANTS_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            query = (
                select(
                    convo.conversation_id,
                    convo.conversation_name,
                    convo.conversation_type,
                    cp.is_pinned,
                    cp.is_favorite,
                )
                .join(cp, cp.conversation_id == convo.conversation_id)
                .where(cp.uid == user_id)
                .where(cp.is_pinned == Constants.YES)
            )
            rows = (await session.execute(query)).all()

        response[Constants.PINNED_STRING_LOWER] = [
            {
                Constants.CONVERSATION_ID: r.conversation_id,
                Constants.CONVERSATION_NAME: r.conversation_name,
                Constants.CONVERSATION_TYPE: r.conversation_type,
                Constants.IS_PINNED: r.is_pinned,
                Constants.IS_FAVORITE: r.is_favorite,
            }
            for r in rows
        ]
        response[Constants.MESSAGE_KEY] = Constants.PINNED_FETCH_SUCCESS_MESSAGE
        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(content=response)


@router.post("/user/get_group_participants")
async def get_group_participants(request: Request):
    """
    Return participants (email and display name) for a group conversation.

    Expected request JSON keys:
        - conversation_id (integer)

    Returns list under key 'participants'.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        data = await request.json()
        conversation_id = data.get("conversation_id")

        if not conversation_id:
            response[
                Constants.MESSAGE_KEY
            ] = Constants.INVALID_REQUEST_PARAMETERS_MESSAGE
            response[Constants.STATUS_CODE_KEY] = Constants.BAD_REQUEST
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        conv_part_model = await db_connect.set_up_table(
            Constants.CONVERSATION_PARTICIPANTS_TABLE
        )
        users_model = await db_connect.set_up_table(Constants.USER_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            query = (
                select(
                    users_model.email,
                    func.concat(
                        users_model.first_name, " ", users_model.last_name
                    ).label("name"),
                )
                .join(conv_part_model, conv_part_model.uid == users_model.uid)
                .where(conv_part_model.conversation_id == conversation_id)
            )

            rows = (await session.execute(query)).all()

            participants = []
            for email, name in rows:
                participants.append(
                    {"email": email, "name": name if name else email.split("@")[0]}
                )

        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        response[Constants.MESSAGE_KEY] = "Group participants fetched successfully"
        response["participants"] = participants

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = "Error fetching group participants"

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/register_device")
async def register_device(request: Request):
    """
    Register a device id for a user to enable push notifications.

    Expected request JSON keys:
        - Constants.EMAIL
        - Constants.DEVICE_ID

    Behavior: associates device_id with user's uid in devices table; returns success or errors.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        data = await request.json()
        email = data.get(Constants.EMAIL)
        device_id = data.get(Constants.DEVICE_ID)

        if not email or not device_id:
            response[
                Constants.MESSAGE_KEY
            ] = Constants.INVALID_REQUEST_PARAMETERS_MESSAGE
            response[Constants.STATUS_CODE_KEY] = Constants.BAD_REQUEST
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        user_model = await db_connect.set_up_table(Constants.USER_TABLE)
        devices_model = await db_connect.set_up_table(Constants.DEVICES_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            async with session.begin():
                query_user = select(user_model.uid).where(user_model.email == email)
                user_result = (await session.execute(query_user)).first()

                if not user_result:
                    response[
                        Constants.MESSAGE_KEY
                    ] = Constants.USER_EXISTENCE_ERROR_MESSAGE
                    response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR
                    return JSONResponse(
                        content=response,
                        status_code=response[Constants.STATUS_CODE_KEY],
                    )

                uid = user_result[0]

                query_device = select(devices_model).where(
                    devices_model.uid == uid, devices_model.device_id == device_id
                )
                existing_device = (await session.execute(query_device)).first()

                if existing_device:
                    response[
                        Constants.MESSAGE_KEY
                    ] = Constants.DEVICE_ALREADY_EXISTS_ERROR
                    response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
                    return JSONResponse(
                        content=response,
                        status_code=response[Constants.STATUS_CODE_KEY],
                    )

                stmt = insert(devices_model).values(uid=uid, device_id=device_id)
                await session.execute(stmt)

        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        response[Constants.MESSAGE_KEY] = Constants.DEVICE_ADDED_SUCCESS

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = Constants.DEVICE_ADD_ERROR

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/unregister_device")
async def unregister_device(request: Request):
    """
    Unregister a previously registered device by device_id.

    Expected request JSON keys:
        - Constants.DEVICE_ID

    Behavior: removes device entry and returns success or appropriate errors.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()

    try:
        data = await request.json()
        device_id = data.get(Constants.DEVICE_ID)

        if not device_id:
            response[
                Constants.MESSAGE_KEY
            ] = Constants.INVALID_REQUEST_PARAMETERS_MESSAGE
            response[Constants.STATUS_CODE_KEY] = Constants.BAD_REQUEST
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        devices_model = await db_connect.set_up_table(Constants.DEVICES_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            async with session.begin():
                query_device = select(devices_model).where(
                    devices_model.device_id == device_id
                )
                device_result = (await session.execute(query_device)).first()

                if not device_result:
                    response[Constants.MESSAGE_KEY] = "Device not found"
                    response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
                    return JSONResponse(
                        content=response,
                        status_code=response[Constants.STATUS_CODE_KEY],
                    )

                delete_stmt = delete(devices_model).where(
                    devices_model.device_id == device_id
                )
                await session.execute(delete_stmt)

        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        response[Constants.MESSAGE_KEY] = "Device unregistered successfully"

    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = "Failed to unregister device"

    return JSONResponse(
        content=response, status_code=response[Constants.STATUS_CODE_KEY]
    )


@router.post("/user/is_favorite")
async def is_favorite(request: Request):
    """
    Return whether a conversation is favorited by the requesting user.

    Expected request JSON keys:
        - Constants.JWT_PARAM_EMAIL
        - Constants.CONVERSATION_ID

    Returns boolean under key 'is_favorite' and a success status.
    """
    response = Constants.RESPONSE_TEMPLATE.copy()
    try:
        input_params = await request.json()

        email = input_params.get(Constants.JWT_PARAM_EMAIL, "").lower()
        conversation_id = input_params.get(Constants.CONVERSATION_ID)

        if not email or not conversation_id:
            response[Constants.STATUS_CODE_KEY] = Constants.BAD_REQUEST
            response[
                Constants.MESSAGE_KEY
            ] = Constants.INVALID_REQUEST_PARAMETERS_MESSAGE
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        user = await db_connect.get_data(Constants.USER_TABLE, email=email)
        if not user:
            response[Constants.STATUS_CODE_KEY] = Constants.USER_EXISTENCE_ERROR
            response[Constants.MESSAGE_KEY] = Constants.USER_EXISTENCE_ERROR_MESSAGE
            return JSONResponse(
                content=response, status_code=response[Constants.STATUS_CODE_KEY]
            )

        user_id = user[Constants.UID]

        cp = await db_connect.set_up_table(Constants.CONVERSATION_PARTICIPANTS_TABLE)

        async with db_connect.AsyncSessionLocal() as session:
            stmt = (
                select(cp.is_favorite)
                .where(cp.conversation_id == conversation_id)
                .where(cp.uid == user_id)
            )
            result = await session.execute(stmt)
            row = result.fetchone()

        is_favorite = False
        if row and row[0] == Constants.YES:
            is_favorite = True

        response[Constants.STATUS_CODE_KEY] = Constants.SUCCESS_CODE
        response[Constants.MESSAGE_KEY] = "Favorite status fetched successfully"
        response["is_favorite"] = is_favorite
        print(response)
        print(input_params)
    except Exception as e:
        print_traceback(e)
        response[Constants.STATUS_CODE_KEY] = Constants.INTERNAL_SERVER
        response[Constants.MESSAGE_KEY] = GlobalData.STATUS_MESSAGE

    return JSONResponse(content=response)
