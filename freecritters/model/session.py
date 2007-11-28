from sqlalchemy.orm import sessionmaker, scoped_session

Session = scoped_session(sessionmaker(autoflush=True, transactional=True))
Session.extension = Session.extension.configure(save_on_init=False)