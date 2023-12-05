from pathlib import Path

basedir = Path(__file__).parent.parent


class BaseConfig:
    SECRET_KEY = "2AZSMss3p5QPbcY2hBsJ"
    WTF_CSRF_SECRET_KEY = "AuwzyszU5sugKN7KZs6f"
    UPLOAD_FOLDER = str(Path(basedir, 'apps', 'images'))


class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"postgresql://self_study_recorder_db_user:yP1bSVmDdFdMdAvzuuoMYw3EU8dmIdwV@dpg-clmout4jtl8s73a73io0-a.singapore-postgres.render.com/self_study_recorder_database"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'testing.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    UPLOAD_FOLDER = str(Path(basedir, 'tests', 'detector', 'images'))


config = {
    'testing': TestingConfig,
    'local': LocalConfig,
}