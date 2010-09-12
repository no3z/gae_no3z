var canvas;

//var stats = new Stats();

var delta = [0,0];
var stage = [window.screenX,window.screenY,window.innerWidth,window.innerHeight];
getBrowserDimensions();


var worldAABB;
var world;
var iterations = 1;
var timeStep = 1 / 20;

var walls = new Array();
var wall_thickness = 200;
var wallsSetted = false;

var text;

var bodies;
var elements;

var createMode = false;
var destroyMode = false;

var isMouseDoubleClick  = false;
var isMouseDown = false;
var mouseJoint;
var mouseX = 0;
var mouseY = 0;
var PI2 = Math.PI * 2;
var inited = false;

init();
//play();
	
if (document.addEventListener) {
  document.addEventListener("DOMContentLoaded", init, false);
}

function init()
{
    if (inited == true)
    {
	for (i = 0; i < bodies.length; i++)
	{
		var body = bodies[i]
		canvas.removeChild( body.GetUserData().element );
		world.DestroyBody(body);
		body = null;
	}

	reset();
    }
    else
    {
	canvas = document.getElementById('canvas');
	
	document.onmousedown = onDocumentMouseDown;
	document.onmouseup = onDocumentMouseUp;
	document.onmousemove = onDocumentMouseMove;
	document.ondblclick = onDocumentDoubleClick;
    
	document.onselectstart = function() {return false;} // ie
	
	// init box2d
	
	worldAABB = new b2AABB();
	worldAABB.minVertex.Set(-200, -200);
	worldAABB.maxVertex.Set( screen.width + 200, screen.height + 200);

	world = new b2World(worldAABB, new b2Vec2(0, 0), true);
		
	setWalls();
	reset();

	play();    
	
	inited = true;
    }
}


function play()
{
	setInterval(loop, 25);	
}

function reset()
{	
bodies = new Array();
elements = new Array();	

	
    var count = document.getElementById('images_count').innerHTML;
    for(var i = 0; i < count; i++)
    {
	createBall(i+1);
    }
}

// .. ACTIONS

function onDocumentMouseDown()
{
	isMouseDown = true;
	return false;
}

function onDocumentMouseUp()
{
	isMouseDown = false;
	return false;
}

function onDocumentMouseMove(e)
{
	var ev = (!e) ? window.event : e;
	mouseX = ev.clientX;
	mouseY = ev.clientY;
}

function onDocumentDoubleClick()
{
    isMouseDoubleClick  = true;
    return false;
//	for (i = 0; i < bodies.length; i++)
//	{
//		var body = bodies[i]
//		canvas.removeChild( body.GetUserData().element );
//		world.DestroyBody(body);
//		body = null;
//	}
//
//	reset();
}

function onElementMouseDown()
{
	return false;
}

function onElementMouseUp()
{
	return false;
}

function onElementClick()
{
	return false;
}
	
function createBall(c)
{
    var x = (x != null) ? x : Math.random() * stage[2];
    var y = (y != null) ? y : Math.random() - 200;

    var factor = 1;

    var element = document.createElement("canvas");
    var graphics = element.getContext("2d");
    var cat = new Image();
    cat.src = document.getElementById("images" + c).name;
    cat.onload= function(){
	
    element.width = cat.width *  factor;
    element.height = cat.height *  factor;	

    graphics.drawImage(cat,0,0);
    };

    element.style['position'] = 'absolute';
    element.style['left'] = -200 + 'px';
    element.style['top'] = -200 + 'px';	
//    element.style['width'] = '15%';
//    element.style['height'] = '15%';	

    canvas.appendChild(element);
    elements.push( element );	
    
    var b2body = new b2BodyDef();	
    var box = new b2BoxDef();
    box.density = 0.20;
    box.friction = 0.17;
    box.restitution = 0.135;

    box.extents.Set((cat.width* factor) >> 1,(cat.height* factor) >> 1);
    b2body.AddShape(box);
    b2body.userData = {element: element, doc: document.getElementById('images' + c)};
    b2body.position.Set(x, y);
    b2body.linearVelocity.Set( Math.random() * 400 - 200, Math.random() * 400 - 200 );
    bodies.push( world.CreateBody(b2body) );
}

//

function loop()
{
	if (getBrowserDimensions())
		setWalls();

	delta[0] += (0 - delta[0]) * .5;
	delta[1] += (0 - delta[1]) * .5;
	
	world.m_gravity.x = 0 + delta[0];
	world.m_gravity.y = 350 + delta[1];
		
	mouseDrag();
	world.Step(timeStep, iterations);	
	
	for (i = 0; i < bodies.length; i++)
	{
		var body = bodies[i];
		var element = elements[i];
		
		element.style['left'] = (body.m_position0.x - (element.width >> 1)) + 'px';
		element.style['top'] = (body.m_position0.y - (element.height >> 1)) + 'px';
		
	/*	if (element.tagName == "DIV")
		{
			// webkit
			text.style['-webkit-transform'] = 'rotate(' + (bodies[i].m_rotation0 * 57.2957795) + 'deg)';
			
			// gecko
			text.style['MozTransform'] = 'rotate(' + (bodies[i].m_rotation0 * 57.2957795) + 'deg)';

			// opera
			element.style['OTransform'] = 'rotate(' + (bodies[i].m_rotation0 * 57.2957795) + 'deg)';
		}
*/
	}
}


// .. BOX2D UTILS

function createBox(world, x, y, width, height, fixed)
{
	if (typeof(fixed) == 'undefined') fixed = true;
	var boxSd = new b2BoxDef();
	if (!fixed) boxSd.density = 1.0;
	boxSd.extents.Set(width, height);
	var boxBd = new b2BodyDef();
	boxBd.AddShape(boxSd);
	boxBd.position.Set(x,y);
	return world.CreateBody(boxBd)
}

function pick_pic()
{

}
	
	var api = 0;

function mouseDrag()
{
	// mouse press
	if (createMode)
	{
	//	createBall( mouseX, mouseY );
	}
	else if (isMouseDown && !mouseJoint)
	{
		var body = getBodyAtMouse();
		
		if (body)
		{
			var md = new b2MouseJointDef();
			md.body1 = world.m_groundBody;
			md.body2 = body;
			md.target.Set(mouseX, mouseY);
			md.maxForce = 30000 * body.m_mass;
			md.timeStep = timeStep;
			mouseJoint = world.CreateJoint(md);
			body.WakeUp();

		    var url = body.GetUserData().doc;
		    api = $(url).qtip("api");
		   
		    api.show();
		}
		else
		{
			createMode = true;
		}
	}
	
	// mouse release
	if (!isMouseDown)
	{
		createMode = false;
		destroyMode = false;
	
		if (mouseJoint)
		{
			world.DestroyJoint(mouseJoint);
			mouseJoint = null;

		    if( api != 0)
		    { api.hide(); api = 0;}
		}
	}
	
	// mouse move
	if (mouseJoint)
	{
		var p2 = new b2Vec2(mouseX, mouseY);
		mouseJoint.SetTarget(p2);
	}

    if(isMouseDoubleClick && !mouseJoint)
    {
	var body = getBodyAtMouse();
	if (body)
	{
	    	    isMouseDoubleClick = false;
	    var url = body.GetUserData().doc.href;
	    var has_music = body.GetUserData().doc.type;
	    if(has_music != 'None') 
	    {
	    	the_audio = document.getElementById('audio_deck');
	    	if(the_audio) 
	    		{
	    			var an = document.getElementById('author_name');
	    			var text = body.GetUserData().doc.title + " / " + body.GetUserData().doc.text;
	    			an.innerHTML = text;
	    			
	    			the_audio.setAttribute('src', has_music);
	    			the_audio.play();
	    			the_audio.addEventListener("load", function() 
	    			{
 						$(".duration span").html(the_audio.duration);
					 	$(".filename span").html(the_audio.src);
					}, true);
					the_audio.load()
	    		}
	    }
	    else
	    	if(url){ window.open(url);}
	    

	}
    }
}

function getBodyAtMouse()
{
	// Make a small box.
	var mousePVec = new b2Vec2();
	mousePVec.Set(mouseX, mouseY);
	
	var aabb = new b2AABB();
	aabb.minVertex.Set(mouseX - 1, mouseY - 1);
	aabb.maxVertex.Set(mouseX + 1, mouseY + 1);

	// Query the world for overlapping shapes.
	var k_maxCount = 10;
	var shapes = new Array();
	var count = world.Query(aabb, shapes, k_maxCount);
	var body = null;
	
	for (var i = 0; i < count; ++i)
	{
		if (shapes[i].m_body.IsStatic() == false)
		{
			if ( shapes[i].TestPoint(mousePVec) )
			{
				body = shapes[i].m_body;
				break;
			}
		}
	}
	return body;
}

function setWalls()
{
	if (wallsSetted)
	{
		world.DestroyBody(walls[0]);
		world.DestroyBody(walls[1]);
		world.DestroyBody(walls[2]);
		world.DestroyBody(walls[3]);
		
		walls[0] = null; 
		walls[1] = null;
		walls[2] = null;
		walls[3] = null;
	}
	
	walls[0] = createBox(world, stage[2] / 2, - wall_thickness, stage[2], wall_thickness);
	walls[1] = createBox(world, stage[2] / 2, stage[3] + wall_thickness, stage[2], wall_thickness);
	walls[2] = createBox(world, - wall_thickness, stage[3] / 2, wall_thickness, stage[3]);
	walls[3] = createBox(world, stage[2] + wall_thickness, stage[3] / 2, wall_thickness, stage[3]);	
	
	wallsSetted = true;
}

// BROWSER DIMENSIONS

function getBrowserDimensions()
{
	var changed = false;
		
	if (stage[0] != window.screenX)
	{
		delta[0] = (window.screenX - stage[0]) * 50;
		stage[0] = window.screenX;
		changed = true;
	}
	
	if (stage[1] != window.screenY)
	{
		delta[1] = (window.screenY - stage[1]) * 50;
		stage[1] = window.screenY;
		changed = true;
	}
	
	if (stage[2] != window.innerWidth)
	{
		stage[2] = window.innerWidth;
		changed = true;
	}
	
	if (stage[3] != window.innerHeight)
	{
		stage[3] = window.innerHeight;
		changed = true;
	}
	
	return changed;
}	

