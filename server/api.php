<?php
    include("config.php");
    $md5 = isset($_GET['md5'])?$_GET['md5']:'';
    $settings = parse_ini_file($config);
    $db = new PDO("sqlite:".$settings['db']);
    $sql = 'select * from video';
    if($md5){
        $sql .= ' where local_md5="'.$md5.'"';
    }
    $output = array();
    foreach ($db->query($sql) as $row){
        $output[] = array(
            'filename' => $row['filename'],
            'title' => $row['title'],
            'duration' => $row['duration'],
            'info' => json_decode($row['info'], true),
            'url' => $row['url'],
            'pic_url' => $row['pic_url'],
            'size' => $row['size']
        );
    }
    header("Content-type: application/json");
    echo json_encode($output);
?>
