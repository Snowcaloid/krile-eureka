class InitLogger:
    content: str = ''

    @classmethod
    def log(cl, message: str) -> None:
        print(message)
        InitLogger.content += f'{message}\n'