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

				<div class="post-meta">
					<?php ieltstask_posted_on(); ?>
				</div>

				<h1><?php the_title(); ?></h1>

				<?php if (has_post_thumbnail()) : ?>
					<figure class="article-card__media">
						<?php the_post_thumbnail('large'); ?>
					</figure>
				<?php endif; ?>

				<div class="entry-content">
					<?php the_content(); ?>
				</div>

				<?php if (has_category() || has_tag()) : ?>
					<div class="entry-taxonomy">
						<?php the_category(' '); ?>
						<?php the_tags('', ' ', ''); ?>
					</div>
				<?php endif; ?>

				<section class="share-panel" aria-label="<?php esc_attr_e('Share this article', 'ieltstask-theme'); ?>">
					<h2 class="share-panel__title"><?php esc_html_e('Share this article', 'ieltstask-theme'); ?></h2>
					<ul class="share-links">
						<?php foreach (ieltstask_get_share_links() as $share_link) : ?>
							<li><a href="<?php echo esc_url($share_link['url']); ?>" target="_blank" rel="noopener noreferrer"><?php echo esc_html($share_link['label']); ?></a></li>
						<?php endforeach; ?>
					</ul>
				</section>

				<?php if (get_the_author_meta('description')) : ?>
					<section class="author-box">
						<h2 class="author-box__title"><?php echo esc_html(get_the_author()); ?></h2>
						<p><?php echo esc_html(get_the_author_meta('description')); ?></p>
					</section>
				<?php endif; ?>
			</article>

			<nav class="post-navigation" aria-label="<?php esc_attr_e('Post navigation', 'ieltstask-theme'); ?>">
				<?php the_post_navigation(); ?>
			</nav>

			<?php
			if (comments_open() || get_comments_number()) {
				comments_template();
			}
			?>
		</div>

		<?php get_sidebar(); ?>
	</div>
	<?php
endwhile;

get_footer();
