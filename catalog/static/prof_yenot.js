var current = 'dfg1';

function show(id) {
	
document.getElementById(current).style.display = 'none';
	document.getElementById(id).style.display = 'block';
	current = id;
} 

var drg;
function newstat(obj) {
obj.className = 'stat_one_act'; 
   if (drg)
drg.className = 'stat_all_act'; 
drg = obj;
}

function email_use2() {
$('.fixed_prof_name').replaceWith( "<div><input class=new_first_name type=text value=" +"'{{ user.first_name }}' >" +
	"<button class=change_first_name >SAVE</button></div>");
	}

function email_use3() {
$('.fixed_prof_email').replaceWith( "<div><input class=new_email type=text value="+"'{{ user.email }}'>" +
	"<button class='change_email'>SAVE</button></div>");
}



window.onclick = function() {

    // AJAX POST
	$('.change_first_name').click(function(){

        $.ajax({
            type: 'POST',
            url: '/catalog/profile/user_update/',
            dataType: 'json',
            data: { 'item': $('.new_first_name').val() ,'field': 'first_name' ,'csrfmiddlewaretoken': '{{ csrf_token }}'},
            success: function(data) {

				$('.first_name').text(data.item)
             
            }
			 window.location.reload(true);
        });

    });
	
	$('.change_email').click(function(){


        $.ajax({
            type: 'POST',
            url: '/catalog/profile/user_update/',
            dataType: 'json',
            data: { 'item': $('.new_email').val() ,'field': 'email' ,'csrfmiddlewaretoken': '{{ csrf_token }}'},
            success: function(data) {

				$('.email').text(data.item)
				window.location.reload(true);
            }
        });

    });
};
