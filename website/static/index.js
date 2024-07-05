

$(document).ready(function() {

    // Functions to perform search
    
    // case the user clicked the search icon
    $('#search_button').click(function() {
        performSearch();
    });

    // case the user pressed enter on the search text area
    $('#search_text').keypress(function(event){
        if (event.which == 13) {
            performSearch();
        }
    });

    // Function to perform search
    
    function performSearch() {
        var search = $('#search_text').val();
        if (search != '') {
            load_data(search);
        } else {
            load_data();
        }
    }

    // "Load the data" this function passes the "query" to the /search route as a POST request
    function load_data(query = '') {
        $.ajax({
            url: "/search",
            method: "POST",
            data: { query: query },  // we will retrieve this 'query' value in the /search route
            success: function(data) {
                $('#result').html(data);
                $('#result').append(data.htmlresponse);
            }
        });
    }

    $('#add_cash').click(function() {
        let float_amount = parseFloat($('#amount').val());
        if (float_amount != '' && float_amount > 0) {
            addCash();
        }
        else {
            window.alert("Please add a positive amount.");
        }
    });

    // case the user pressed enter on the search text area
    $('#amount').keypress(function(event){
        if (event.which == 13) {
            let float_amount = parseFloat($('#amount').val());
            if (float_amount != '' && float_amount > 0) {
                addCash();
            }
            else {
                window.alert("Please add a positive amount.");
            }
        }
    });


    function addCash(){
        amount = $('#amount').val();
        
        let userConfirmation = confirm(`Are you sure you want to add $${amount} to your current balance?`);
        if (userConfirmation)
        {
            $.ajax({
                url: "/update_cash",
                method: "POST",
                data: {amount: amount},
                success: function(data) 
                {
                    alert(data.message)
                },
                error: function(data)
                {
                    alert(data.message)
                }
            })
        }
    }

    // function to redirect user to details of movie
    window.seeDetails = function(movieID) {
        window.location.href = "/details/" + movieID;
    }

    // function to add a movie to favorites
    window.addToFavorites = function(movieid) {
    $.ajax({
      url: "/add_to_favorites",
      method: "POST",
      data: { movieid: movieid },
      success: function (data) {
        alert(data.message);
      },
      error: function (xhr, status, error) {
        alert("Error: " + error);
      },
    });
  }


    // Function to buy movies
    window.buyMovie = function(movieID, title, type, price) {
        
        let userConfirmation = confirm(`Are you sure you want to buy this movie?\n ${type}: ${title}.\n Price: $ ${price}`);

        if (userConfirmation)
        {
            $.ajax({
                url: "/buy_movie",
                method: "POST",
                data: {movieID: movieID , title: title, price: price},
                success: function(data) 
                {
                    alert(data.message)
                },
                error: function(data)
                {
                    alert(data.message)
                }
            })
        }
        
    }

});
