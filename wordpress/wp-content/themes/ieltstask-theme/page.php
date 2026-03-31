<?php
if (! defined('ABSPATH')) {
	exit;
}

get_header();

while (have_posts()) :
	the_post();
	?>
	<article <?php post_class('article-card'); ?>>
		<h1><?php the_title(); ?></h1>

		<div class="page-content">
			<?php the_content(); ?>
		</div>
	</article>
	<?php
endwhile;

get_footer();
