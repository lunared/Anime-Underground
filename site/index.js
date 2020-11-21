const express = require('express');
const { find } = require('lodash');
const fs = require('fs');

const app = express();
const Kitsu = require('./backends/kitsu');

const kitsu = new Kitsu();

app.set('views', __dirname + '/views');
app.set('view engine', 'jsx');
app.engine('jsx', require('express-react-views').createEngine());

app.get('/', async (req, res, next) => {
    const {
        query: {
            quality = 'high',
            language = 'en',
        }
    } = req;

    const anime = JSON.parse(fs.readFileSync(`${__dirname}/schedule.json`, 'utf8'));

    const watched = await kitsu.fetchAnime(anime.watched);
    const schedule = await kitsu.fetchAnime(anime.schedule.map(({ id }) => id));
    const lineup = {
        watched: anime.watched.map(
            (id) => find(watched, { 'id': id }) || { id },
        ),
        schedule: anime.schedule.map(
            ({ id, time, episode = 1 }) => ({
                ...(find(schedule, { 'id': id }) || { id }),
                time,
                episode,
            }),
        ),
    };
    const resolution = quality === 'low' ? "480p" : "720p"
    const root = `${req.protocol}://${req.hostname}`;
    res.render('index', {
        brand: 'Anime Underground',
        tagline: 'Live Fridays @ 9pm EST',
        language,
        quality,
        streamRoot: `${root}/hls/animeunderground.m3u8`,
        stream: `${root}/hls/animeunderground_${resolution}/index.m3u8`,
        streamFallback: `${root}/hls/animeunderground_480p/index.m3u8`,
        lineup,
    });

    next();
});

app.listen(8080, () => {
    console.log(`Ready to serve from port ${8080}`);
});
