const React = require('react');

function Document({ title, children }) {
    return (
        <html>
            <head>
                <title>{title}</title>
                <link href="https://fonts.googleapis.com/css?family=Raleway:400,300,600" rel="stylesheet" type="text/css" />
                <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.css" />
                <link rel="stylesheet" type="text/css" href="/static/style.css" />
                <link href="http://vjs.zencdn.net/5.10.8/video-js.css" rel="stylesheet" />

                <script src="https://cdn.jsdelivr.net/hls.js/latest/hls.light.min.js"></script>
            </head>
            <body>
                {children}
            </body>
        </html>
    );
}

function Player({ streamUrl }) {
    return (
        <div style={{
            "textAlign":"center"
        }}>
            <video id="stream" className="video-js" controls preload="auto" width="1280" height="720" poster="/static/notplaying.jpg">
            </video>
            <script dangerouslySetInnerHTML={{__html: `
                if(Hls.isSupported()) {
                    var video = document.getElementById('stream');
                    var hls = new Hls();
                    hls.loadSource('${streamUrl}');
                    hls.attachMedia(video);
                    hls.on(Hls.Events.MANIFEST_PARSED,function() {
                        video.play();
                    });
                }    
            `}} />
        </div>
    )
}

function WatchList({ lineup, language }) {
    const Row = ({ show }) => {
        const {
            id,
            link,
            titles: {
                [language]: title,
            } = { [language]: id},
            thumbnail,
            synopsis,
            genres = [],
            episodeCount,
        } = show;
        return (
            <tr>
                <td>
                    <a className="tooltip" href={link}>
                        { title }
                        <div className="tooltip-text">
                            <img src={thumbnail} style={{ "float": "left", "width": "45%" }}/>
                            <div style={{
                                "float":"left",
                                "width": "50%",
                                "paddingLeft": "5%",
                            }}>
                                { synopsis }
                            </div>
                        </div>
                    </a>
                </td>
                <td>{ genres.join(', ') }</td>
                <td style={{"textAlign": "center"}}>{ episodeCount }</td>
            </tr>
        )
    }

    const list = lineup.map(
        show => <Row show={show}></Row>
    );

    return (
        <table className="u-full-width" >
            <thead>
                <tr>
                    <th>Show</th>
                    <th>Genre</th>
                    <th>Episode</th>
                </tr>
            </thead>
            <tbody>
                {list}
            </tbody>
        </table>
    );
}

function Schedule({ lineup, language }) {
    const Row = ({ timeslot }) => {
        const {
            id,
            link,
            titles: {
                [language]: title,
            } = { [language]: id},
            thumbnail,
            synopsis,
            genres = [],
            time,
            episode,
            episodeCount,
        } = timeslot;
        return (
            <tr>
                <td>
                    <a className="tooltip" href={link}>
                        { title }
                        <div className="tooltip-text">
                            <img src={thumbnail} style={{"float":"left", "width": "45%" }}/>
                            <div style={{
                                "float":"left",
                                "width": "50%",
                                "paddingLeft": "5%",
                            }}>
                                { synopsis }
                            </div>
                        </div>
                    </a>
                </td>
                <td>{ genres.join(', ') }</td>
                <td>{ time }</td>
                <td>{ episode} / {episodeCount}</td>
            </tr>
        );
    };

    const schedule = lineup.map((timeslot) => 
        <Row timeslot={timeslot}></Row>
    );

    return (
        <table className="u-full-width" >
            <thead>
                <tr>
                    <th>Show</th>
                    <th>Genre</th>
                    <th>Time*</th>
                    <th>Episode</th>
                </tr>
            </thead>
            <tbody>
                { schedule }
            </tbody>
        </table>
    )
}

function Body({
    brand,
    tagline,
    stream,
    streamRoot,
    language,
    quality,
    lineup,
    chat,
}) {
  return (
    <Document title={`${brand} - ${tagline}`}>
        <div className="container">
            <div id="title" className="row">
                <h1>{ brand }</h1>&nbsp;
                <h5>{ tagline }</h5>
            </div>
            <div className="row" id="player">
                <Player streamUrl={stream}></Player>
            </div>
            <div className="row">
                <div className="five columns">
                    <input className="u-full-width" type="text" id="rtmp_link" value={ streamRoot } disabled />
                </div>
                <div className="four columns">
                    <a className={ "button" + (quality === 'high' ? ' button-primary' : '') }
                        href={`/?language=${language}&quality=high`}
                    >HD</a>&nbsp;
                    <a className={ "button" + (quality !== 'high' ? ' button-primary' : '') }
                        href={`/?language=${language}&quality=low`}
                    >Low</a>
                </div>
                <div className="three columns">
                    <a href={ chat } className="button button-discord u-pull-right u-full-width">
                        Join Chat
                    </a>
                </div>
            </div>
            <div className="row u-text-center"></div>
            <div className="row">
                <h3>Schedule<span>*Start times are an estimation and may be off by a few minutes</span></h3>
                <Schedule lineup={lineup.schedule} language={language}></Schedule>
            </div>
            <div className="row">
                <div className="six columns">
                    <h5>Previously Watched</h5>
                </div>
                <div className="six columns">
                    <a className={ "button" + (language == 'en' ? " button-primary" : "") }
                    href={`/?language=en&quality=${quality}`}>
                        English
                    </a>&nbsp;
                    <a className={ "button" + (language == 'canonical' ? " button-primary" : "") }
                    href={`/?language=canonical&quality=${quality}`}>
                        Canonical
                    </a>&nbsp;
                    <a className={ "button" + (language == 'jp' ? " button-primary" : "") }
                    href={`/?language=jp&quality=${quality}`}>
                        Japanese
                    </a>
                </div>
                <WatchList lineup={lineup.watched} language={language}></WatchList>
            </div>
            <div className="row">
                <span className="u-pull-right">Anime metadata provided by <a href="https://kitsu.io" title="Kitsu">Kitsu</a></span>
            </div>
        </div>
    </Document>
  )
}

module.exports = Body;
