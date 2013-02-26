'use strict';

var express = require('express'),
    app = express(),
    fs = require('fs'),
    util = require('util');

module.exports = app;

function errorHandler(err, req, res, next){
    console.log(err.message);
    res.send(err.status || 400, err.message);
}

app.configure(function(){
    app.use(express.bodyParser());
    app.use(express.methodOverride());
    app.use(express.logger());
    app.use(app.router);
    app.use(errorHandler);
});

app.use('/static', express.static(__dirname + '/static'));

app.set('view engine', 'hbs');


app.get('/health-check', function(req, res){
    res.send('OK');
});

app.get('/', function(req, res, next){
    res.sendfile(__dirname + '/static/html/main.html');
});

app.post('/audio', function(req, res, next){
    var file = req.files.audioFile,
        filename;

    filename = file.name;
    if(!filename){
        return res.redirect('/play/sample.mp3');
    }

    fs.readFile(file.path, function(err, data){
        fs.writeFile(__dirname + '/static/audio/' + filename, data, function(err){
            if(err){
                console.log('Error writing file: ' + err);
            }
            res.redirect('/play/' + filename);
        });
    });
});

app.get('/play/:filename?', function(req, res, next){
    var filename = req.params.filename || 'sample.mp3';
    res.render('play', {'filename': filename}, function(err, html){
        if(err){
            console.log('Error rendering html: ' + err);
        }
        res.send(html);
    });
});

app.listen(80);
