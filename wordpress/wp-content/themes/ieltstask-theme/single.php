<?php
if (! defined('ABSPATH')) {
	exit;
}

get_header();

while (have_posts()) :
	the_post();
	?>
	<article <?php post_class('article-card'); ?>>
		<div class="post-meta">
			<?php ieltstask_posted_on(); ?>
		</div>

		<h1><?php the_title(); ?></h1>

		<?php if (has_post_thumbnail()) : ?>
			<?php the_post_thumbnail('large'); ?>
		<?php endif; ?>

		<div class="entry-content">
			<?php the_content(); ?>
		</div>

		<div class="entry-taxonomy">
			<?php the_category(', '); ?>
			<?php the_tags('<p>', ' ', '</p>'); ?>
		</div>
	</article>

	<div class="post-navigation">
		<?php the_post_navigation(); ?>
	</div>

	<?php
	if (comments_open() || get_comments_number()) {
		comments_template();
	}
endwhile;

get_footer();
