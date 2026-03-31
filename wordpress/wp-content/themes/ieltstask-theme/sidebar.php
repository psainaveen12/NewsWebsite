<?php
if (! defined('ABSPATH')) {
	exit;
}
?>
<aside class="site-sidebar" aria-label="<?php esc_attr_e('Sidebar', 'ieltstask-theme'); ?>">
	<?php if (is_active_sidebar('primary-sidebar')) : ?>
		<?php dynamic_sidebar('primary-sidebar'); ?>
	<?php else : ?>
		<section class="sidebar-card">
			<h2 class="sidebar-card__title"><?php esc_html_e('Search the site', 'ieltstask-theme'); ?></h2>
			<?php get_search_form(); ?>
		</section>

		<section class="sidebar-card">
			<h2 class="sidebar-card__title"><?php esc_html_e('Latest Posts', 'ieltstask-theme'); ?></h2>
			<ul class="sidebar-list">
				<?php
				wp_get_archives(
					[
						'type'  => 'postbypost',
						'limit' => 5,
					]
				);
				?>
			</ul>
		</section>

		<section class="sidebar-card">
			<h2 class="sidebar-card__title"><?php esc_html_e('Site Policies', 'ieltstask-theme'); ?></h2>
			<ul class="sidebar-list">
				<?php foreach (ieltstask_get_legal_links() as $link) : ?>
					<li><a href="<?php echo esc_url($link['url']); ?>"><?php echo esc_html($link['label']); ?></a></li>
				<?php endforeach; ?>
			</ul>
		</section>

		<section class="sidebar-card">
			<h2 class="sidebar-card__title"><?php esc_html_e('Editorial note', 'ieltstask-theme'); ?></h2>
			<p><?php esc_html_e('Independent editorial content, transparent ad placement, and migration-safe publishing controls remain part of the WordPress build because they are explicit in the Blogger XML.', 'ieltstask-theme'); ?></p>
		</section>
	<?php endif; ?>
</aside>
