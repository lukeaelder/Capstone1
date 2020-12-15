// Navbar

$(".nav-menu").on("mouseenter", function(){
    if ($(".nav-menu-dropdown").hasClass("dropdown-closed")){
        $(".nav-menu-dropdown").toggleClass("dropdown-closed").toggleClass("dropdown-open")
    }
    if ($(".nav-profile-dropdown").hasClass("dropdown-open")){
        $(".nav-profile-dropdown").toggleClass("dropdown-closed").toggleClass("dropdown-open")
    }
});

$(".nav-profile").on("mouseenter", function(){
    if ($(".nav-profile-dropdown").hasClass("dropdown-closed")){
        $(".nav-profile-dropdown").toggleClass("dropdown-closed").toggleClass("dropdown-open")
    }
    if ($(".nav-menu-dropdown").hasClass("dropdown-open")){
        $(".nav-menu-dropdown").toggleClass("dropdown-closed").toggleClass("dropdown-open")
    }
});

$(".nav-search, .nav-favorites, .nav-bookmarks, .nav-settings, .nav-logo, .navbar-login-signup").on("mouseenter", function(){
    if ($(".nav-profile-dropdown").hasClass("dropdown-open")){
        $(".nav-profile-dropdown").toggleClass("dropdown-closed").toggleClass("dropdown-open")
    }
    if ($(".nav-menu-dropdown").hasClass("dropdown-open")){
        $(".nav-menu-dropdown").toggleClass("dropdown-closed").toggleClass("dropdown-open")
    }
});


$(".navbar").on("mouseleave", function(){
    if ($(".nav-menu-dropdown").hasClass("dropdown-open")){
        $(".nav-menu-dropdown").toggleClass("dropdown-closed").toggleClass("dropdown-open")
    }
    if ($(".nav-profile-dropdown").hasClass("dropdown-open")){
        $(".nav-profile-dropdown").toggleClass("dropdown-closed").toggleClass("dropdown-open")
    }
})

// Play Trailer

$(".play-trailer").on("click", function(){
    const key = $(".videowrapper").attr("key")
    $(".videowrapper").html(`<iframe class="trailer" src="https://www.youtube.com/embed/${key}" frameborder="0"></iframe>`)
    $(window).scrollTop(0);
    $("body").css("overflow", "hidden")
    $(".videowrapper").css("display", "block")
});

$(".videowrapper").on("click", function(e){
    if (e.target.nodeName != "iframe"){
        $(".videowrapper").html("")
        $("body").css("overflow", "auto")
        $(".videowrapper").css("display", "none")
    }
});

// User Selection Bar

$(".selection-list").on("click", function(){
    if ($(".user-lists").hasClass("hide")){
        $(".user-lists").toggleClass("hide").toggleClass("show")
    }
    if ($(".user-favorites").hasClass("show")){
        $(".user-favorites").toggleClass("hide").toggleClass("show")
    }
})

$(".selection-favorites").on("click", function(){
    if ($(".user-lists").hasClass("show")){
        $(".user-lists").toggleClass("hide").toggleClass("show")
    }
    if ($(".user-favorites").hasClass("hide")){
        $(".user-favorites").toggleClass("hide").toggleClass("show")
    }
})

// List creation

async function queryMovies(){
    const URL = window.location.origin
    const query = $(".list-search").val()
    movies = await axios.post(`${URL}/list/movies`, {"query": query})
    appendSearchResults(movies)
}

function appendSearchResults(movies){
    $(".list-search-results").empty()
    for (let i = 0; i < 10; i++){
        $(".list-search-results").append(`
        <div class="list-search-result" data-id="${movies.data[i].id}">
            <p class="list-search-title">${movies.data[i].title}</p>
            <p class="list-search-year">${movies.data[i].release_date}</p>
        </div>
        `)
    }
}

let typingTimer;
let typingInterval = 300;
let $input = $(".list-search");

$input.on("keyup", function(){
    clearTimeout(typingTimer);
    typingTimer = setTimeout(queryMovies, typingInterval)
    if ($(this).val() == ""){
        $(".list-search-results").empty()
    }
});

$input.on("keydown", function(){
    clearTimeout(typingTimer);
});

if (top.location.pathname === "/movies/upcoming" || top.location.pathname === "/movies/top_rated" ||
    top.location.pathname === "/movies/popular" || top.location.pathname === "/movies/now_playing"){
    $(window).on("scroll", function() {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
            moreResults()
        }
    });
};

let page = 2;

async function moreResults(){
    const URL = window.location.origin
    const section = $(".main").attr("data-section")
    movies = await axios.post(`${URL}/movie/section/more`, {"section": section, "page": page})
    page++;
    appendSectionResults(movies)
}

function appendSectionResults(movies){
    for (let i = 0; i < movies.data.length; i++){
        let vote;
        let poster;
        if (movies.data[i].vote_average != 0){
            vote = `<div class="rating color${Math.round(movies.data[i].vote_average)}">
                        <p>${movies.data[i].vote_average}</p>
                    </div>`
        } else {
            vote = `<div class="rating color0">
                        <p>NR</p>
                    </div>`
        }
        if (movies.data[i].poster_path){
            poster = `<img loading="lazy" src="https://image.tmdb.org/t/p/w500${movies.data[i].poster_path}" alt="" class="movie-poster-full">`
        } else {
            poster = `<img loading="lazy" src="/static/images/no-image.JPG" alt="" class="movie-poster-full">`
        }
        $(".movie-posters-full").append(`
        <a href="/movie/${movies.data[i].id}">
                <div class="movie-card">
                    ${vote}
                    ${poster}
                    <p class="movie-title">${movies.data[i].title}</p>
                    <p class="release-date">${movies.data[i].release_date}</p>
                </div>
            </a>
        `)
    }
}

if (top.location.pathname === "/list/new"){
    $(document).on("click", ".list-search-result" ,async function(){
        const movie_id = $(this).attr("data-id")
        const URL = window.location.origin
        movie = await axios.post(`${URL}/checkmovie`, {"movie_id": movie_id})
        $(".list-search-results").empty()
        $(".list-search").val("")
        appendListItem(movie)
    })

    let grid = new Muuri(".grid", {
        dragEnabled: true,
        dragSort: true,
        dragStartPredicate: function (item, Event) {
            if (Event.target.matches(".list-delete-button")) {
                return false;
            }
            return true;
       }
    });

    function refreshItems(){
        grid.refreshSortData();
        grid.synchronize();
        grid.refreshItems()

    }

    grid.on("dragEnd", function(){
        grid.refreshItems()
    })

    $(document).on("click", ".list-delete-button" ,function(e){
        grid.remove(grid.getItems($(this).parents(".item").index()), {removeElements: true})
        refreshItems();
    });

    function appendListItem(movie){
        if (movie.data.poster_path){
            poster = `<img loading="lazy" src="https://image.tmdb.org/t/p/w500${movie.data.poster_path}" alt="" class="list-poster">`
        } else {
            poster = `<img loading="lazy" src="/static/images/no-image.JPG" alt="" class="list-poster">`
        }
        let item = document.createElement('div')
        item.className = "item"
        item.innerHTML = `<div class="item-content" data-id="${movie.data.id}">
                            ${poster}
                            <p class="list-text">${movie.data.title}</p>
                            <p class="list-delete-button">X</p>
                        </div>`
        grid.add(item)
        refreshItems()
    }

    $(".create-list-button").on("click", async function(){
        if ($("input[name='title']").val().length === 0 || grid.getItem(0) === null){
            $(".list-errors").text("Make sure you list has a title and movies in it")
            return false
        }
        if ($("input[name='title']").val().length > 50){
            $(".list-errors").text("Title cant be more than 50 character")
            return false
        }
        if ($("input[name='title']").val().length > 100){
            $(".list-errors").text("Description cant be more than 100 character")
            return false
        }
        $(".create-list-button").remove()
        let allGrid = grid.getItems()
        const URL = window.location.origin
        let moviePositions = []
        let title = $("input[name='title']").val()
        let description = $("textarea[name='description']").val()
        for (let i = 0; i < allGrid.length; i++){
            let movie = allGrid[i]._element.children[0]
            let movie_id = $(movie).attr("data-id")
            let movie_position = i + 1
            moviePositions.push({movie_id: movie_id, movie_position: movie_position})
        }
        list = await axios.post(`${URL}/createlist`, {"list": moviePositions, "title": title, "description": description})
        window.location.replace(`${URL}/goto/myself`);
    })
}