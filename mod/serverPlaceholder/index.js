const express = require('express')
const app = express()
const port = 5000

app.use(express.json());


battleToken = 0

app.post('/sendEvent', (req, res) => {
    req.body.events.forEach(event => {
        if (event.EventName == 'OnEndLoad') {
            console.log(event);
            console.log("Send new token: " + battleToken);
            res.send(`${battleToken++}`)
        } else {
            console.log('EventName: ' + event.EventName);
            console.log('Token: ' + event.Token);
            console.log(event)
        }

        console.log('_____________________________\n\n');
    });

    res.status(200).end()
})


app.get('/', (req, res) => {
    res.send('Work fine')
})

app.listen(port, () => {
    console.log(`Server placeholder start at http://localhost:${port}`)
})