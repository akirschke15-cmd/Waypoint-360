---
name: frontend-patterns
description: React patterns including composition, compound components, render props, custom hooks, state management, performance optimization, memoization, code splitting, virtualization, forms, animations, and accessibility.
origin: ECC
version: 2.2
---

# Frontend Patterns Skill

Production-grade React patterns for scalable, performant, accessible UIs.

## When to Activate

- Building React components
- Structuring state management
- Optimizing performance
- Handling complex forms
- Implementing animations
- Building accessible interfaces

## Component Composition

### Functional Components with Hooks

```typescript
interface UserCardProps {
  userId: string
  onUpdate?: (user: User) => void
}

export function UserCard({ userId, onUpdate }: UserCardProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadUser()
  }, [userId])

  async function loadUser() {
    try {
      setLoading(true)
      const data = await fetchUser(userId)
      setUser(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Skeleton />
  if (error) return <Error message={error} />
  if (!user) return <NotFound />

  return (
    <div className="user-card">
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <button onClick={() => onUpdate?.(user)}>Update</button>
    </div>
  )
}
```

### Compound Components

Share state between related components.

```typescript
// Dialog.tsx
interface DialogContextType {
  isOpen: boolean
  onOpen: () => void
  onClose: () => void
}

const DialogContext = createContext<DialogContextType | null>(null)

export function Dialog({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <DialogContext.Provider value={{ isOpen, onOpen: () => setIsOpen(true), onClose: () => setIsOpen(false) }}>
      {children}
    </DialogContext.Provider>
  )
}

export function DialogTrigger({ children }: { children: React.ReactNode }) {
  const context = useContext(DialogContext)
  return <button onClick={context?.onOpen}>{children}</button>
}

export function DialogContent({ children }: { children: React.ReactNode }) {
  const context = useContext(DialogContext)
  if (!context?.isOpen) return null
  return (
    <div className="dialog-overlay" onClick={context.onClose}>
      <div className="dialog" onClick={e => e.stopPropagation()}>
        {children}
      </div>
    </div>
  )
}

// Usage
<Dialog>
  <DialogTrigger>Open Dialog</DialogTrigger>
  <DialogContent>
    <h2>Dialog Content</h2>
  </DialogContent>
</Dialog>
```

### Render Props Pattern

Pass render function for maximum flexibility.

```typescript
interface RenderProps<T> {
  data: T
  loading: boolean
  error: string | null
}

interface DataFetcherProps<T> {
  url: string
  children: (props: RenderProps<T>) => React.ReactNode
}

export function DataFetcher<T>({ url, children }: DataFetcherProps<T>) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(url)
      .then(r => r.json())
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [url])

  return children({ data: data as T, loading, error })
}

// Usage
<DataFetcher<User> url="/api/users/123">
  {({ data, loading, error }) =>
    loading ? <Skeleton /> : error ? <Error /> : <UserInfo user={data} />
  }
</DataFetcher>
```

## Custom Hooks

### Data Fetching Hook

```typescript
interface UseFetchOptions {
  method?: 'GET' | 'POST' | 'PATCH'
  body?: any
  skip?: boolean
}

export function useFetch<T>(
  url: string,
  options?: UseFetchOptions
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(!options?.skip)
  const [error, setError] = useState<Error | null>(null)

  const fetch = useCallback(async () => {
    try {
      setLoading(true)
      const response = await fetch(url, {
        method: options?.method || 'GET',
        ...(options?.body && { body: JSON.stringify(options.body) })
      })
      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }, [url])

  useEffect(() => {
    if (!options?.skip) fetch()
  }, [url, options?.skip])

  return { data, loading, error, refetch: fetch }
}

// Usage
const { data: user, loading, error, refetch } = useFetch<User>('/api/users/123')
```

### Form Hook

```typescript
interface UseFormOptions<T> {
  initialValues: T
  onSubmit: (values: T) => Promise<void>
}

export function useForm<T extends Record<string, any>>({
  initialValues,
  onSubmit
}: UseFormOptions<T>) {
  const [values, setValues] = useState(initialValues)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setValues(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }, [])

  const handleBlur = useCallback((e: React.FocusEvent<HTMLInputElement>) => {
    setTouched(prev => ({
      ...prev,
      [e.target.name]: true
    }))
  }, [])

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      setIsSubmitting(true)
      try {
        await onSubmit(values)
      } catch (err) {
        setErrors({ submit: err.message })
      } finally {
        setIsSubmitting(false)
      }
    },
    [values, onSubmit]
  )

  return { values, errors, touched, isSubmitting, handleChange, handleBlur, handleSubmit }
}

// Usage
const form = useForm({
  initialValues: { name: '', email: '' },
  onSubmit: async (values) => {
    await createUser(values)
  }
})
```

## State Management

### Context + useReducer (Built-in)

```typescript
interface State {
  user: User | null
  isLoading: boolean
  error: string | null
}

type Action =
  | { type: 'SET_USER'; payload: User }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }

function userReducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload }
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    default:
      return state
  }
}

const UserContext = createContext<[State, React.Dispatch<Action>] | null>(null)

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(userReducer, {
    user: null,
    isLoading: false,
    error: null
  })

  return (
    <UserContext.Provider value={[state, dispatch]}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (!context) throw new Error('useUser must be in UserProvider')
  return context
}
```

### Zustand (External Library)

```typescript
import { create } from 'zustand'

interface UserStore {
  user: User | null
  setUser: (user: User) => void
  clearUser: () => void
}

export const useUserStore = create<UserStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  clearUser: () => set({ user: null })
}))

// Usage
const user = useUserStore((state) => state.user)
const setUser = useUserStore((state) => state.setUser)
```

## Performance Optimization

### Memoization

```typescript
// Memoize component
const UserCard = memo(function UserCard({ user }: { user: User }) {
  return <div>{user.name}</div>
})

// Memoize value
const memoizedValue = useMemo(() => {
  return expensiveComputation(data)
}, [data])

// Memoize callback
const handleClick = useCallback(() => {
  dispatch(action)
}, [action])
```

### Code Splitting

```typescript
import { lazy, Suspense } from 'react'

const AdminPanel = lazy(() => import('./AdminPanel'))

export function App() {
  const [showAdmin, setShowAdmin] = useState(false)

  return (
    <>
      <button onClick={() => setShowAdmin(true)}>Admin</button>
      {showAdmin && (
        <Suspense fallback={<Skeleton />}>
          <AdminPanel />
        </Suspense>
      )}
    </>
  )
}
```

### Virtualization (Large Lists)

```typescript
import { FixedSizeList } from 'react-window'

export function UserList({ users }: { users: User[] }) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      {users[index].name}
    </div>
  )

  return (
    <FixedSizeList
      height={600}
      itemCount={users.length}
      itemSize={35}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  )
}
```

## Form Handling

```typescript
interface FormValues {
  email: string
  password: string
  rememberMe: boolean
}

export function LoginForm() {
  const form = useForm<FormValues>({
    initialValues: { email: '', password: '', rememberMe: false },
    onSubmit: async (values) => {
      await login(values)
    }
  })

  return (
    <form onSubmit={form.handleSubmit}>
      <input
        type="email"
        name="email"
        value={form.values.email}
        onChange={form.handleChange}
        onBlur={form.handleBlur}
      />
      {form.touched.email && form.errors.email && (
        <span className="error">{form.errors.email}</span>
      )}

      <input
        type="password"
        name="password"
        value={form.values.password}
        onChange={form.handleChange}
      />

      <label>
        <input
          type="checkbox"
          name="rememberMe"
          checked={form.values.rememberMe}
          onChange={form.handleChange}
        />
        Remember me
      </label>

      <button type="submit" disabled={form.isSubmitting}>
        {form.isSubmitting ? 'Signing in...' : 'Sign In'}
      </button>
    </form>
  )
}
```

## Animations

### CSS Transitions

```typescript
export function Modal({ isOpen }: { isOpen: boolean }) {
  return (
    <div className={`modal ${isOpen ? 'open' : ''}`}>
      <div className="modal-content">Content</div>
    </div>
  )
}

// CSS
.modal {
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s, visibility 0.2s;
}

.modal.open {
  opacity: 1;
  visibility: visible;
}
```

### Framer Motion

```typescript
import { motion } from 'framer-motion'

export function AnimatedList({ items }: { items: string[] }) {
  return (
    <motion.ul layout>
      {items.map((item) => (
        <motion.li
          key={item}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          {item}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

## Accessibility

```typescript
export function Button({
  children,
  onClick,
  ariaLabel
}: {
  children: React.ReactNode
  onClick: () => void
  ariaLabel?: string
}) {
  return (
    <button
      onClick={onClick}
      aria-label={ariaLabel}
      className="button"
    >
      {children}
    </button>
  )
}

// Form field with label
export function TextField({
  label,
  error,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label: string
  error?: string
}) {
  const id = useId()

  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <input id={id} {...props} aria-invalid={!!error} />
      {error && <span role="alert">{error}</span>}
    </div>
  )
}
```

## Production Checklist

- [x] Components properly memoized
- [x] No unnecessary re-renders
- [x] Large lists virtualized
- [x] Code splitting on route/feature boundaries
- [x] Images optimized and lazy-loaded
- [x] Accessibility: labels, ARIA, keyboard navigation
- [x] Forms validated and have clear errors
- [x] Loading states for all async operations
- [x] Error boundaries catch component errors
- [x] Performance audited (Lighthouse, profiler)
