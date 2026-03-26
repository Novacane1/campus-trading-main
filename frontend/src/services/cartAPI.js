import api from './api'

const cartAPI = {
  getCart: () => {
    return api.get('/cart')
  },

  addToCart: (itemId) => {
    return api.post('/cart', { item_id: itemId })
  },

  removeFromCart: (cartId) => {
    return api.delete(`/cart/${cartId}`)
  },

  clearCart: () => {
    return api.delete('/cart/clear')
  },

  getCartCount: () => {
    return api.get('/cart/count')
  },

  batchRemove: (cartIds) => {
    return api.post('/cart/batch-remove', { cart_ids: cartIds })
  }
}

export default cartAPI
