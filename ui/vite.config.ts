import { sveltekit } from '@sveltejs/kit/vite'
import { defineConfig } from 'vite'
import { enhancedImages } from '@sveltejs/enhanced-img'
import Icons from 'unplugin-icons/vite'
import tailwindcss from '@tailwindcss/vite'
import { config as dotEnvConfig } from 'dotenv'

// have to configure dotenv to load correct .env file
dotEnvConfig({ path: `.env.${process.env.NODE_ENV}` })

export default defineConfig({
	build: {
		rollupOptions: {
			output: {
				// split mapbox & deck.gl into their own chunk; they are huge
				manualChunks: function (id) {
					if (id.includes('mapbox-gl') || id.includes('deck.gl')) {
						return 'map-vendor'
					}
				}
			}
		}
	},
	plugins: [tailwindcss(), enhancedImages(), sveltekit(), Icons({ compiler: 'svelte' })]
})
