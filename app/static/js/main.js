$(document).ready(function()
{
	//Disable tabs in the navigation
	$('li.disabled > a').click(function(e) {
		e.preventDefault();
		return false;
	});
});