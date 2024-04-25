const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
    app.use('/web', createProxyMiddleware({
        target: 'http://localhost:5500',
        changeOrigin: true
    }));
};