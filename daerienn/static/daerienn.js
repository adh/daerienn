daerienn_commands = {}

daerienn_commands["replace"] = function(cmd){
    id = cmd["id"];
    v = cmd["v"];
    document.getElementById(id).outerHTML = v;
};

(function (){
    function process_command(cmd){
	daerienn_commands[cmd["op"]](cmd);
    }
    
    function process_response(data){
	console.log(data);
	d = JSON.parse(data);
	d.forEach(process_command)
    }

    function submit_handler(ev){
	fd = new FormData(ev.target.form);
	fd.append("dae-xhr-trigger", ev.target.id)
	xhr = new XMLHttpRequest();
	xhr.open("POST", "");
	xhr.onreadystatechange = function(){
	    
	    if (xhr.readyState == 4){
		if (xhr.status != 200){
		    alert("XMLHTTPRequest failed");
		}
		
		process_response(xhr.responseText);
	    }
	}
	xhr.send(fd);
	ev.preventDefault();
    }
    
    function register_event_hooks(e){
	e.on('submit', submit_handler);
	e.find('button[type=submit]').on('click', submit_handler);
    }
    
    $('.dae-toplevel').each(function(idx, e){
	register_event_hooks($(e))
    });
})();
