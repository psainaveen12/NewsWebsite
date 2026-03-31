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
		<h2 class="comments-area__title">
			<?php
			printf(
				/* translators: %s: number of comments */
				esc_html(_nx('%s comment', '%s comments', get_comments_number(), 'comments title', 'ieltstask-theme')),
				esc_html(number_format_i18n(get_comments_number()))
			);
			?>
		</h2>

		<ol class="comment-list">
			<?php
			wp_list_comments(
				[
					'style'       => 'ol',
					'short_ping'  => true,
					'avatar_size' => 56,
				]
			);
			?>
		</ol>

		<?php the_comments_navigation(); ?>
	<?php endif; ?>

	<?php if (! comments_open() && get_comments_number()) : ?>
		<p class="comments-closed"><?php esc_html_e('Comments are closed.', 'ieltstask-theme'); ?></p>
	<?php endif; ?>

	<?php
	comment_form(
		[
			'class_submit' => 'button-link',
			'title_reply'  => __('Leave a comment', 'ieltstask-theme'),
		]
	);
	?>
</section>
