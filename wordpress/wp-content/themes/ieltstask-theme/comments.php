<?php
if (! defined('ABSPATH')) {
	exit;
}

if (post_password_required()) {
	return;
}
?>

<section class="comments-area">
	<?php if (have_comments()) : ?>
		<h2><?php esc_html_e('Comments', 'ieltstask-theme'); ?></h2>
		<ol class="comment-list">
			<?php wp_list_comments(); ?>
		</ol>
	<?php endif; ?>

	<?php comment_form(); ?>
</section>
