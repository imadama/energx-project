import { resolve } from 'path'
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        laadpaal: resolve(__dirname, 'energx-laadpaal.html'),
        blog: resolve(__dirname, 'blog.html'),
        'blog-isde': resolve(__dirname, 'blog/isde-subsidie-warmtepomp.html'),
        'blog-ratio-zaptec': resolve(__dirname, 'blog/ratio-vs-zaptec.html'),
        'blog-installatie': resolve(__dirname, 'blog/laadpaal-installatie-dag.html'),
        warmtepomp: resolve(__dirname, 'energx-warmtepomp.html'),
        thuisbatterij: resolve(__dirname, 'energx-thuisbatterij.html'),
        'blog-thuisbatterij-kopen': resolve(__dirname, 'blog-thuisbatterij-kopen.html'),
      },
    },
  },
})
