$(document).ready(function(){
    /* attach a submit handler to the form */
    $("#form").submit(function(event) {

        /* stop form from submitting normally */
        event.preventDefault(); 
        
        /* Send the data using post and put the results in a div */
        $.post("php/contacts.php", $("#form").serialize(),function(result){
            $('#result').html(result);
        });
    }); 
});
    