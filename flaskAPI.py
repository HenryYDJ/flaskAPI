# This is the entry point of the program

# WARNING：
#       Before deploying to actual server, change the secret key!

# Todo:
#   1. Implement logger

from app import create_app

app = create_app()

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True, host="0.0.0.0")
=======
    # app.run(debug=True, host="0.0.0.0")
    app.run(debug=True, host="0.0.0.0", ssl_context=('novaqbit.com.pem', 'novaqbit.com.key'))
>>>>>>> 5ea832f2a9b023e8130918387f435ad810348299
