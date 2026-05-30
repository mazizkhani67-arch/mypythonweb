<?php

/* SECTION I - CONFIGURATION */

$receiver_mail = 'example@mail.com';

/* SECTION II - CODE */

if ( !empty ( $_POST['name'] ) && !empty ( $_POST [ 'email' ] ) && !empty ( $_POST [ 'message' ] ) && ($_POST['name']<>'name')
        && ($_POST['email']<>'e-mail') && ($_POST['message']<>'message')) {
    $subject = $_POST['name'];
    $email   = $_POST['email'];
    $message = $_POST['message'];
    $subject = 'From website';
    $header  = 'From: ' . $_POST['name'] . '\r\nReply-To: ' . $email . '';
    if ( mail( $receiver_mail, $subject, $message, $header ) )
        $result = '<div class="success">Your message was successfully sent.</div>';
    else
        $result = '<div class="fail">We are sorry but your message could not be sent.';
} else {
    $result = 'Please fill all the fields in the form.';
}
//header('Location: ' . preg_replace('/\?.*/', '', $_SERVER['HTTP_REFERER']) . '?result=' . urlencode($result));
echo $result ;
?>
