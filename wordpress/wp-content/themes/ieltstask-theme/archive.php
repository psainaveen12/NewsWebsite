<?php
if (! defined('ABSPATH')) {
	exit;
}

get_header();
?>

<header class="hero">
	<p class="hero__eyebrow"><?php esc_html_e('Archive', 'ieltstask-theme'); ?></p>
	<h1 class="page-title"><?php the_archive_title(); ?></h1>
	<?php the_archive_description('<p class="page-intro">', '</p>'); ?>
</header>

<div class="content-grid">
	<div class="content-primary">
		<?php ieltstask_breadcrumbs(); ?>

		<section class="post-grid">
			<?php if (have_posts()) : ?>
				<?php
				while (have_posts()) :
					the_post();
					?>
					<article <?php post_class('post-card'); ?>>
						<?php if (has_post_thumbnail()) : ?>
							<a class="post-card__media" href="<?php the_permalink(); ?>">
								<?php the_post_thumbnail('large'); ?>
							</a>
						<?php endif; ?>

						<div class="post-meta">
							<?php ieltstask_posted_on(); ?>
						</div>

						<h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
						<?php the_excerpt(); ?>
					</article>
				<?php endwhile; ?>

				<div class="pagination">
					<?php the_posts_pagination(['mid_size' => 1]); ?>
				</div>
			<?php else : ?>
				<article class="post-card">
					<h2><?php esc_html_e('Nothing here yet', 'ieltstask-theme'); ?></h2>
				</article>
			<?php endif; ?>
		</section>
	</div>

	<?php get_sidebar(); ?>
</div>

<?php
get_footer();
