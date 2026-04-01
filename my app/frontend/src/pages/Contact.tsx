import { useState, useEffect } from 'react'

interface MenuItem {
  id: number
  name: string
  ingredients: string
  day: string
}

interface GroceryItem {
  id: number
  name: string
  quantity: string
  purchased: boolean
}

const MENU_API = 'http://localhost:8000/api/menu'
const GROCERY_API = 'http://localhost:8000/api/grocery'

export default function Contact() {
  const [activeTab, setActiveTab] = useState<'menu' | 'grocery'>('menu')
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [groceryItems, setGroceryItems] = useState<GroceryItem[]>([])
  const [newMenuName, setNewMenuName] = useState('')
  const [newMenuIngredients, setNewMenuIngredients] = useState('')
  const [newMenuDay, setNewMenuDay] = useState('')
  const [newGroceryItem, setNewGroceryItem] = useState('')
  const [newGroceryQty, setNewGroceryQty] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchMenuItems()
    fetchGroceryItems()
  }, [])

  const fetchMenuItems = async () => {
    try {
      setError('')
      const response = await fetch(MENU_API)
      if (!response.ok) throw new Error('Failed to fetch menu')
      const data = await response.json()
      setMenuItems(data.items || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load menu')
    }
  }

  const fetchGroceryItems = async () => {
    try {
      setError('')
      const response = await fetch(GROCERY_API)
      if (!response.ok) throw new Error('Failed to fetch grocery list')
      const data = await response.json()
      setGroceryItems(data.items || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load grocery list')
    }
  }

  const addMenuItem = async () => {
    if (!newMenuName || !newMenuDay) {
      setError('Please fill in meal name and day')
      return
    }

    try {
      setError('')
      const response = await fetch(MENU_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newMenuName,
          ingredients: newMenuIngredients,
          day: newMenuDay,
        }),
      })

      if (!response.ok) throw new Error('Failed to add menu item')
      const data = await response.json()
      setMenuItems([...menuItems, data.item])
      setNewMenuName('')
      setNewMenuIngredients('')
      setNewMenuDay('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add menu item')
    }
  }

  const deleteMenuItem = async (id: number) => {
    try {
      setError('')
      const response = await fetch(`${MENU_API}/${id}`, { method: 'DELETE' })
      if (!response.ok) throw new Error('Failed to delete item')
      setMenuItems(menuItems.filter(item => item.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete item')
    }
  }

  const addGroceryItem = async () => {
    if (!newGroceryItem) {
      setError('Please enter item name')
      return
    }

    try {
      setError('')
      const response = await fetch(GROCERY_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newGroceryItem,
          quantity: newGroceryQty || '1',
        }),
      })

      if (!response.ok) throw new Error('Failed to add grocery item')
      const data = await response.json()
      setGroceryItems([...groceryItems, data.item])
      setNewGroceryItem('')
      setNewGroceryQty('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add grocery item')
    }
  }

  const toggleGroceryPurchased = async (id: number) => {
    try {
      setError('')
      const response = await fetch(`${GROCERY_API}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })

      if (!response.ok) throw new Error('Failed to update item')
      const data = await response.json()
      setGroceryItems(groceryItems.map(item => item.id === id ? data.item : item))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update item')
    }
  }

  const deleteGroceryItem = async (id: number) => {
    try {
      setError('')
      const response = await fetch(`${GROCERY_API}/${id}`, { method: 'DELETE' })
      if (!response.ok) throw new Error('Failed to delete item')
      setGroceryItems(groceryItems.filter(item => item.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete item')
    }
  }

  const purchasedCount = groceryItems.filter(item => item.purchased).length
  const totalGrocery = groceryItems.length

  return (
    <div className="grocery-container">
      <h1>Menu & Grocery</h1>

      {error && <div className="error-message">{error}</div>}

      <div className="grocery-tabs">
        <button
          className={`tab-button ${activeTab === 'menu' ? 'active' : ''}`}
          onClick={() => setActiveTab('menu')}
        >
          📋 Weekly Menu
        </button>
        <button
          className={`tab-button ${activeTab === 'grocery' ? 'active' : ''}`}
          onClick={() => setActiveTab('grocery')}
        >
          🛒 Grocery List
        </button>
      </div>

      {activeTab === 'menu' ? (
        <div className="menu-section">
          <div className="add-menu-section">
            <h2>Add Meal</h2>
            <div className="add-menu-form">
              <input
                type="text"
                placeholder="Meal name (e.g., Spaghetti)"
                value={newMenuName}
                onChange={(e) => setNewMenuName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addMenuItem()}
              />
              <input
                type="text"
                placeholder="Ingredients (comma separated)"
                value={newMenuIngredients}
                onChange={(e) => setNewMenuIngredients(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addMenuItem()}
              />
              <select
                value={newMenuDay}
                onChange={(e) => setNewMenuDay(e.target.value)}
              >
                <option value="">Select Day</option>
                <option value="Monday">Monday</option>
                <option value="Tuesday">Tuesday</option>
                <option value="Wednesday">Wednesday</option>
                <option value="Thursday">Thursday</option>
                <option value="Friday">Friday</option>
                <option value="Saturday">Saturday</option>
                <option value="Sunday">Sunday</option>
              </select>
              <button onClick={addMenuItem}>Add Meal</button>
            </div>
          </div>

          <div className="menu-list-section">
            <h2>This Week's Menu</h2>
            {menuItems.length === 0 ? (
              <p className="empty-state">No meals planned yet!</p>
            ) : (
              <div className="menu-grid">
                {menuItems.map(item => (
                  <div key={item.id} className="menu-card">
                    <div className="menu-day">{item.day}</div>
                    <h3>{item.name}</h3>
                    {item.ingredients && (
                      <p className="ingredients">{item.ingredients}</p>
                    )}
                    <button
                      onClick={() => deleteMenuItem(item.id)}
                      className="delete-button-small"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="grocery-section">
          <p className="grocery-stats">Purchased: {purchasedCount} of {totalGrocery} items</p>

          <div className="add-grocery-section">
            <h2>Add Item to Grocery List</h2>
            <div className="add-grocery-form">
              <input
                type="text"
                placeholder="Item name (e.g., Milk)"
                value={newGroceryItem}
                onChange={(e) => setNewGroceryItem(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addGroceryItem()}
              />
              <input
                type="text"
                placeholder="Quantity (e.g., 1 gallon)"
                value={newGroceryQty}
                onChange={(e) => setNewGroceryQty(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addGroceryItem()}
              />
              <button onClick={addGroceryItem}>Add Item</button>
            </div>
          </div>

          <div className="grocery-list-section">
            <h2>Shopping List</h2>
            {groceryItems.length === 0 ? (
              <p className="empty-state">Grocery list is empty!</p>
            ) : (
              <ul className="grocery-list">
                {groceryItems.map(item => (
                  <li
                    key={item.id}
                    className={`grocery-item ${item.purchased ? 'purchased' : ''}`}
                  >
                    <div className="grocery-content">
                      <input
                        type="checkbox"
                        checked={item.purchased}
                        onChange={() => toggleGroceryPurchased(item.id)}
                        className="grocery-checkbox"
                      />
                      <div className="grocery-details">
                        <span className="grocery-name">{item.name}</span>
                        {item.quantity && (
                          <span className="grocery-qty">{item.quantity}</span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => deleteGroceryItem(item.id)}
                      className="delete-button"
                    >
                      Delete
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
