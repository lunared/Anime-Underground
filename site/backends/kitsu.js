const axios = require('axios');
const { chunk, find } = require('lodash');

const pageSize = 20

class KitsuBackend {
    constructor () {
        this.client = axios.create({
            baseURL: 'http://kitsu.io/api/edge',
            headers: {
                'Accept': 'application/vnd.api+json',
                'Content-Type': 'application/vnd.api+json',
            }
        });
        // dumb in memory cache
        this.seriesCache = {};
        this.genres = []
    }

    /**
     * Get kitsu's genre list
     */
    async fetchGenres() {
        if (this.genres.length === 0) {
            const {
                data: {
                    data: result,
                },
            } = await this.client.get(
                '/genres',
                {
                    params: {
                        'fields[genres]': 'name',
                        'page[limit]': 500,
                    },
                }
            );
            this.genres = result;
            return result;
        }
        return this.genres;
    }

    /**
     * Fetches anime metadata from a list of series ids
     * Results are requested in pages and cached
     * @param {*} series 
     */
    async fetchAnime(series) {

        const resultSet = [];
        const fetch = [];

        series.forEach(id => {
            const cached = this.seriesCache[id];
            if (cached) {
                resultSet.push(cached);
            } else {
                fetch.push(id);
            }
        });

        if (fetch.length <= 0) {
            return resultSet;
        }

        const genres = await this.fetchGenres();
        let results = []
        for (let batch of chunk(fetch, pageSize)) {
            const { 
                data: {
                    data: result
                },                
            } = await this.client.get(
                '/anime',
                {
                    params: {
                        'filter[slug]': batch.join(','),
                        'fields[anime]': [
                            'slug',
                            'posterImage',
                            'canonicalTitle',
                            'titles',
                            'synopsis',
                            'genres',
                            'episodeCount',
                        ].join(','),
                        'include': 'genres',
                        'page[limit]': pageSize
                    },
                }
            );
            results = results.concat(result);
        }

        results.forEach((show) => {
            const {
                attributes: {
                    slug,
                    canonicalTitle = slug,
                    titles: {
                        en_jp = canonicalTitle,
                        en = en_jp,
                        ja_jp: jp = canonicalTitle
                    },
                    posterImage: {
                        tiny: thumbnail = null,
                    },
                    episodeCount = 1,
                    synopsis = '',
                },
                relationships: {
                    genres: {
                        data: seriesGenres,
                    },
                },
            } = show;

            const meta = {
                id: slug,
                link: `https://kitsu.io/anime/${slug}`,
                titles: {
                    en,
                    jp,
                    canonical: canonicalTitle,
                },
                thumbnail,
                episodeCount,
                synopsis,
                genres: seriesGenres.map(
                    ({ id }) => find(genres, { 'id': id }).attributes.name,
                )
            };
            this.seriesCache[slug] = meta;
            resultSet.push(meta);
        });
        return resultSet;
    }
}

module.exports = KitsuBackend;
