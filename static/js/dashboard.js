$(document).ready(function() {
    $('#suggested-skills-container').infinite({
        // Customize options as needed
        itemSelector: '.col-md-3',  // Selector for each item
        loading: {
            msgText: "<em>Loading more skills...</em>",
            finishedMsg: "<em>No more skills to load.</em>",
        },
        errorCallback: function() {
            // Handle error if necessary
        }
    });
});
