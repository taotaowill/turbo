# encoding: utf-8
import turbo

# server
PORT = 8880

# mongo
turbo.config({
    "MONGO": "mongodb://127.0.0.1:27017/"
})

