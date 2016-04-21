<?php
	header('Content-type: text/html; charset=UTF-8');
	include('lib/emoji.php');
	$data = shell_exec('python gettheweather.py');
	
	$char_count = strlen($data);
	
?>

<!DOCTYPE html>
<html lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html" charset="UTF-8">
	<title>Ride The Weather - VC York</title>
	<style>
		* {
			box-sizing: border-box;
		}
		body{
			background: #e0e0e0;
			color: #666;
			font-size: 29px;
			font-family: Garamond, Baskerville, 'Baskerville Old Face', 'Hoefler Text', 'Times New Roman', serif;
			line-height: 1.6em;
		}
		div.container{
			max-width: 860px;
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translateX(-50%) translateY(-50%);
		}
		div.forecast{
			background: #fff;
			padding: 2em;
			margin-bottom: .5em;
		}
		p.chars{
			text-align: right;
			font-size: 17px;
		}
	</style>
</head>

<body>
	<div class="container">
		<div class="forecast">
			<?php	echo($data); ?>
		</div>
		<p class="chars"><?php echo($char_count); ?> characters</p>
	</div>
</body>
</html>


