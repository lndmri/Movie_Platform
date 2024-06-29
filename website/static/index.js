

$(document).ready(function() {

    // Functions to perform search
    
    // case the user clicked the search icon
    $('#search_button').click(function() {
        performSearch();
    });

    // case the user pressed enter on the serach text area
    $('#search_text').keypress(function(event){
        if (event.which == 13) {
            performSearch();
        }
    });

    // Function to perfrom search
    
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
});
