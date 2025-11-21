import uvicorn
from src.commons.config_manager import cfg
from src.constants.constants import Constants

def app_start():
    uvicorn.run(
        "src.app:app",  
        host=cfg.get_env_config(Constants.HOSTNAME),
        port=int(cfg.get_env_config(Constants.PORT)),
        reload=True
    )

if __name__ == "__main__":
    app_start()
