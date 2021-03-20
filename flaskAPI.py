# This is the entry point of the program

# WARNING：
#       Before deploying to actual server, change the secret key!

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
