# Gideon AI Landing Page Design Guidelines

## Design Philosophy
The Gideon AI landing page follows a clean, spacious aesthetic inspired by Apple's design principles, emphasizing clarity, breathing room, and sophisticated simplicity.

## Color Palette
- **Background**: `#FAFAF9` - Warm off-white
- **Text Primary**: `#1E1E1E` - Near black
- **Text Secondary**: `#666666` - Medium gray
- **Text Muted**: `#A8A8A8` - Light gray
- **Primary (Accent)**: `#c68642` - Copper/burnt orange
- **Primary Hover**: `#b57638` - Darker copper
- **White**: `#FFFFFF` - Pure white for cards
- **Border Light**: `#E5E5E0` - Subtle borders

## Typography
### Font Families
- **Headlines**: Playfair Display (serif) - Weight 500
- **Body & UI**: Inter (sans-serif) - Weight 400-600

### Font Sizes
- **H1**: 3rem → 4rem → 5rem (mobile → tablet → desktop)
- **H2**: 2rem → 2.5rem → 3rem
- **H3**: 1.25rem → 1.5rem
- **Body**: 1.125rem → 1.25rem
- **Section Labels**: 0.75rem uppercase with 0.15em letter-spacing

### Spacing
- **Margins**: Generous margins between elements (mb-8, mb-12, mb-16)
- **Line Height**: 1.75-1.8 for optimal readability

## Layout Principles
### Container
- Max width: 1280px
- Padding: 64px (desktop), 32px (mobile)

### Sections
- Full height sections: `min-h-screen` with `py-32` padding
- Consistent vertical rhythm with ample white space
- Alternating backgrounds (white/off-white)

### Grid & Spacing
- Grid gaps: 12-20 (48px-80px)
- Card padding: 48px horizontal, 40px vertical
- Section spacing: 32 (128px) vertical padding

## Component Patterns
### Navigation
- Transparent floating navbar
- Large logo (text-4xl)
- Generous internal padding (py-8)
- No background, minimal visual weight

### Buttons
- Primary: Copper background, white text, rounded corners
- Padding: 18px 40px
- Hover: Subtle lift with shadow
- Font size: 16px

### Cards
- White background with subtle shadow
- Large padding (48px 40px)
- Rounded corners (16px)
- Hover effect with shadow and slight lift

### Images
- Contained within sections, not cropped
- Consistent height (256px for cards)
- Object-contain for full visibility

## Content Strategy
### Voice & Tone
- Clear, direct, professional
- Focus on outcomes and benefits
- Psychological angle emphasized

### Section Flow
1. Hero - Bold question/statement
2. Value Props - Three key benefits
3. How It Works - Four-step process
4. Orange Banner - Problem/solution contrast
5. Methodology - Data sources
6. Framework - Freudian model
7. Capabilities - What agents simulate
8. CTA - Final push to action

## Animation & Interactions
- Smooth transitions (0.2s-0.3s)
- Hover states on all interactive elements
- Scale transforms on hover (1.05)
- Shadow depth changes

## Responsive Design
- Mobile-first approach
- Consistent spacing ratios
- Typography scales smoothly
- Grid collapses gracefully

## Key Design Decisions
1. **Spaciousness over density** - Let content breathe
2. **Subtle over bold** - Refined color usage
3. **Typography hierarchy** - Clear visual structure
4. **Consistent rhythm** - Predictable spacing patterns
5. **Quality over quantity** - Every element has purpose

## Technical Notes
- Uses Tailwind CSS for styling
- Next.js Image component for optimization
- Component-based architecture
- CSS variables for theming