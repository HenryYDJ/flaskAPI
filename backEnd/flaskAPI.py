# This is the entry point of the program

# WARNING：
#       Before deploying to actual server, change the secret key!

# Todo:
#   1. Implement logger

from app import create_app

app = create_app()

if __name__ == '__main__':
    # app.run(debug=True, host="0.0.0.0")
    app.run(debug=True, host="0.0.0.0", ssl_context=('./backEnd/novaqbit.com.pem', './backEnd/novaqbit.com.key'))
