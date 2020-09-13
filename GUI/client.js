// tcp_client
const net = require('net');

const options = {
    port: 5005
};

const client = net.createConnection(options, () => {
    client.write('connection established\r\n');
});

// supply data through shell
client.on('data', data => {
    console.log(data.toString());
    client.end();
})