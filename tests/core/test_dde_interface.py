# these imports are provided by pywin32
if sys.platform == "win32":
    import win32con  # type: ignore
    import win32process  # type: ignore
    import win32ui  # type: ignore
    import dde  # type: ignore


server = dde.CreateServer()
server.Create("Client")
conversation = dde.CreateConversation(server)


