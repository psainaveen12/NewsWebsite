<?php
if (! defined('ABSPATH')) {
	exit;
}

get_header();
?>

<section class="hero">
	<p class="hero__eyebrow"><?php esc_html_e('404', 'ieltstask-theme'); ?></p>
	<h1><?php esc_html_e('Page not found', 'ieltstask-theme'); ?></h1>
	<p><?php esc_html_e('The page may have moved during migration. Check redirect mappings or search for the topic below.', 'ieltstask-theme'); ?></p>
</section>

<div class="content-grid">
	<div class="content-primary">
		<article class="post-card">
			<?php ieltstask_breadcrumbs(); ?>
			<?php get_search_form(); ?>
		</article>
	</div>

	<?php get_sidebar(); ?>
</div>

<?php
get_footer();
