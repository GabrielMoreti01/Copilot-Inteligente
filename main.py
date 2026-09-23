"""Start the local web application; no camera/microphone access on the server."""
if __name__ == '__main__':
    import uvicorn
    uvicorn.run('copiloto_app.api:app', host='127.0.0.1', port=8000)
