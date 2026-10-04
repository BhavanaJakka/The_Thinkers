
const _ = require('lodash');
const axios = require('axios');
const fetch = require('node-fetch');
const ejs = require('ejs');
const jwt = require('jsonwebtoken');
const minimist = require('minimist');

// 5 Reachable attack path call sites:
_.merge({}, { a: 1 });
axios.get('https://example.com/api');
fetch('https://example.com/data');
ejs.render('<h1><%= user %></h1>', { user: 'Admin' });
jwt.verify('sample.token.str', 'secret');

// minimist is imported but not called with vulnerable options
