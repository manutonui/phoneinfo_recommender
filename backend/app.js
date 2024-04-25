require('dotenv').config()
const express = require('express')
const app = express()
const server = require("http").createServer(app);
const PORT = process.env.PORT
// const cors = require('cors');

app.use(express.json())

site = 'https://litcode.xyz'
nlp_api = `${site}/nlp`
recommender_api =  `${site}/recommender`


let allowedOrigins = [site]
if (process.env.ENV === 'DEV') {
    recommender_api =  `http://127.0.0.1:5001`
    nlp_api = `http://127.0.0.1:5002`
    allowedOrigins = ['http://localhost:3000']
}

// app.use(cors());
app.use(( req, res, next) => { // logs all requests
    console.log(req.path, req.method)
    next()
})

const io = require('socket.io')(server, {
    path: '/socket.io',
    cors: {
        origin: allowedOrigins
    }
})

io.on('connection', (socket) => {
    console.log(`Socket [${socket.id}] connected`)

    socket.on('sendmessage', async (data)=>{
        req_body = {input: data.data}
        try {
            const options = {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(req_body) // Convert data to JSON string
            }
            fetch(`${nlp_api}/parse_preferences`, options).then( response => {
                if (!response.ok) {return "Response Error!"}
                return response.json()
            }).then(data => {
                console.log(data)
                fetch_from_api(data, recommender_api, 'get_recommendations', socket)
            }).catch(e => {
                console.log('err: ', e)
            })
        } catch (e) {
            console.log('Error parsing: ', e)
        }
    })
})

const fetch_from_api = async (req_body, api, endpoit, socket) => {
    try {
        const options = {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(req_body)
        }

        fetch(`${api}/${endpoit}`, options).then(response => {
            if (!response.ok) { return "Respnse err!!!" }
            return response.json()
        }).then(data => {
            // console.log("Data retrieved: ", data)
            socket.emit('delivermessage', data)
            // return data
        }).catch(e => {
            console.log('err: ', e)
            return "err: "+e
        })
    } catch (e) {
        console.log(`Error receiving response for [${req_body}] [${api}] api after [${endpoint}]. Error: ${e}`)
        return e
    }
}

// middleware to catch non-existing routes e.g render page '404 Not Found'
app.use((req, res, next) => {
    res.status(404).json({error: "[!] Route doesn't exist"})
});

server.listen(PORT, ()=>{
    console.log("[!] App listening on port: ",PORT)
})