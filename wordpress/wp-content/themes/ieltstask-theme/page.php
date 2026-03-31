<?php
if (! defined('ABSPATH')) {
	exit;
}

get_header();

while (have_posts()) :
	the_post();
	?>
	<div class="content-grid">
		<div class="content-primary">
			<article <?php post_class('article-card'); ?>>
				<?php ieltstask_breadcrumbs(); ?>
				<h1><?php the_title(); ?></h1>

				<div class="page-content">
					<?php the_content(); ?>
				</div>
			</article>
		</div>

		<?php get_sidebar(); ?>
	</div>
	<?php
endwhile;

get_footer();
