<?php
if (! defined('ABSPATH')) {
	exit;
}

get_header();
?>

<?php if (is_home() && ! is_paged()) : ?>
	<section class="hero">
		<p class="hero__eyebrow"><?php esc_html_e('IELTS preparation platform', 'ieltstask-theme'); ?></p>
		<h1><?php bloginfo('name'); ?></h1>
		<p><?php esc_html_e('Practice-driven IELTS reading, writing, speaking, and listening resources with a cleaner WordPress publishing flow and a layout that stays close to the existing Blogger experience.', 'ieltstask-theme'); ?></p>
	</section>
<?php else : ?>
	<header class="hero">
		<p class="hero__eyebrow"><?php esc_html_e('Content archive', 'ieltstask-theme'); ?></p>
		<h1 class="page-title"><?php single_post_title(); ?></h1>
	</header>
<?php endif; ?>

<div class="content-grid">
	<div class="content-primary">
		<div class="section-heading">
			<p class="section-heading__eyebrow"><?php esc_html_e('Latest posts', 'ieltstask-theme'); ?></p>
			<h2 class="section-heading__title"><?php esc_html_e('Fresh IELTS resources and updates', 'ieltstask-theme'); ?></h2>
		</div>

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
					<h2><?php esc_html_e('No posts found', 'ieltstask-theme'); ?></h2>
					<p><?php esc_html_e('This theme is ready, but content still needs to be imported or published.', 'ieltstask-theme'); ?></p>
				</article>
			<?php endif; ?>
		</section>
	</div>

	<?php get_sidebar(); ?>
</div>

<?php
get_footer();
