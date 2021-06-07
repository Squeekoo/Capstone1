const BASE_URL = window.location.host;
const songList = $('#song-list');
const songResults = $("#song-results");

async function getSongs(evt) {
    evt.preventDefault();
    try {
        let songQuery = $("#song-query").val();
        let res = await axios.post(`${BASE_URL}/songs`, JSON.stringify({ songQuery }),
            {
                headers: {
                    'content-type': 'application/json'
                }
            });

        handleResponse(res);
    } catch (err) {
        console.error(err);
    }
};

function buildHTML(song, idx) {
    return `
            <li class="eachSong" data-id="${song.id}" data-index="${idx}">
                <img src="${song.album.images[2].url}" id="song-img">
                <div class="name-artist">
                    <a href="${song.external_urls.spotify}">
                        ${song.name}
                    </a>
                    -
                    <a href="${song.artists[0].external_urls.spotify}">
                        ${song.artists[0].name}
                    </a>
                </div>

                <button class="btn btn-sm select-song" data-id="${song.id}" data-index="${idx}">SELECT</button>                
            </li>
            `
};

function handleResponse(res) {
    let songInfo = res.data.songs.tracks.items;
    const eachSong = songInfo.map((song) => song);

    songList.html("");

    eachSong.forEach((song, idx) => {
        songList.append(buildHTML(song, idx));
    });

    $(".select-song").click(selectSong);

    async function selectSong() {
        const idxID = $(this).data('index');
        const jsonSongData = encodeURIComponent(JSON.stringify(eachSong[idxID]));
        const decodeJSONSongData = JSON.parse(decodeURIComponent(jsonSongData));
        console.log(decodeJSONSongData);

        songList.html(buildHTML(eachSong[idxID], idxID));

        $("#post-form").append(`<input type="hidden" id="json-input" name="song-data" value="${decodeJSONSongData.id}" data-json="${jsonSongData}">`);

        $(".select-song").hide();

    };
};

$("#search-song").click(getSongs);




