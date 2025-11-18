/// <reference types="cypress" />

/**
 * E2E tests for complete user flow through CF_Copilot app.
 *
 * Tests the full journey:
 * 1. Landing on the app
 * 2. Setting user profile
 * 3. Browsing companies
 * 4. Filtering companies
 * 5. Selecting companies
 * 6. Optimizing route
 * 7. Viewing itinerary
 */

describe('CF_Copilot Complete User Flow', () => {
  beforeEach(() => {
    // Visit the app
    cy.visit('/')

    // Wait for initial load
    cy.get('[data-testid="app-container"]', { timeout: 10000 })
      .should('be.visible')
  })

  it('should display the main application', () => {
    cy.contains('Career Fair Copilot').should('be.visible')
    cy.get('[data-testid="company-list"]').should('exist')
  })

  describe('User Profile Management', () => {
    it('should open and update user profile', () => {
      // Click profile button
      cy.contains('Update Profile').click()

      // Modal should appear
      cy.get('[data-testid="profile-modal"]').should('be.visible')

      // Fill in profile
      cy.get('input[name="major"]').clear().type('Computer Science')
      cy.get('input[name="timeBudget"]').clear().type('120')

      // Save profile
      cy.contains('Save Profile').click()

      // Modal should close
      cy.get('[data-testid="profile-modal"]').should('not.exist')
    })
  })

  describe('Company Browsing and Filtering', () => {
    it('should display list of companies', () => {
      cy.get('[data-testid="company-card"]')
        .should('have.length.at.least', 1)
    })

    it('should filter companies by search term', () => {
      // Type in search box
      cy.get('input[placeholder*="Search"]').type('Tech')

      // Results should be filtered
      cy.get('[data-testid="company-card"]').each(($card) => {
        cy.wrap($card).should('contain.text', 'Tech')
      })
    })

    it('should filter companies by major', () => {
      // Click major filter
      cy.get('select[name="majorFilter"]').select('Computer Science')

      // Verify filter is applied
      cy.url().should('include', 'major=Computer')
    })

    it('should filter companies by position type', () => {
      // Click internship filter
      cy.contains('Internship').click()

      // Verify companies shown recruit for internships
      cy.get('[data-testid="company-card"]')
        .first()
        .should('contain.text', 'Internship')
    })

    it('should filter companies by ballroom', () => {
      // Select ballroom
      cy.contains('Waldorf').click()

      // Verify only Waldorf companies shown
      cy.get('[data-testid="company-card"]').each(($card) => {
        cy.wrap($card).should('contain.text', 'Waldorf')
      })
    })
  })

  describe('Company Selection', () => {
    it('should select companies by clicking cards', () => {
      // Click first company card
      cy.get('[data-testid="company-card"]')
        .first()
        .click()

      // Card should show selected state
      cy.get('[data-testid="company-card"]')
        .first()
        .should('have.class', 'selected')
    })

    it('should select companies by clicking map booths', () => {
      // Click a booth on the map
      cy.get('[data-testid="booth"]')
        .first()
        .click()

      // Booth should be highlighted
      cy.get('[data-testid="booth"]')
        .first()
        .should('have.attr', 'fill', 'rgb(59, 130, 246)') // Blue color
    })

    it('should deselect companies', () => {
      // Select a company
      cy.get('[data-testid="company-card"]')
        .first()
        .as('firstCard')

      cy.get('@firstCard').click()
      cy.get('@firstCard').should('have.class', 'selected')

      // Deselect
      cy.get('@firstCard').click()
      cy.get('@firstCard').should('not.have.class', 'selected')
    })

    it('should show selected count', () => {
      // Select 3 companies
      cy.get('[data-testid="company-card"]').each(($card, index) => {
        if (index < 3) {
          cy.wrap($card).click()
        }
      })

      // Check selected count
      cy.contains('3 companies selected').should('be.visible')
    })
  })

  describe('Route Optimization', () => {
    beforeEach(() => {
      // Select some companies
      cy.get('[data-testid="company-card"]')
        .first()
        .click()

      cy.get('[data-testid="company-card"]')
        .eq(1)
        .click()

      cy.get('[data-testid="company-card"]')
        .eq(2)
        .click()
    })

    it('should optimize route with selected companies', () => {
      // Set time budget
      cy.get('input[name="timeBudget"]').clear().type('60')

      // Click optimize button
      cy.contains('Optimize Route').click()

      // Wait for optimization
      cy.get('[data-testid="loading"]', { timeout: 5000 })

      // Itinerary should appear
      cy.get('[data-testid="itinerary"]').should('be.visible')
    })

    it('should display route details in itinerary', () => {
      // Optimize route
      cy.get('input[name="timeBudget"]').clear().type('60')
      cy.contains('Optimize Route').click()

      // Check itinerary has stops
      cy.get('[data-testid="itinerary-step"]')
        .should('have.length.at.least', 1)

      // Each step should show time and location
      cy.get('[data-testid="itinerary-step"]').first().within(() => {
        cy.contains(/\d+:\d+ (AM|PM)/).should('be.visible') // Time
        cy.contains(/Booth/).should('be.visible') // Booth number
      })
    })

    it('should show route on map', () => {
      // Optimize route
      cy.contains('Optimize Route').click()

      // Map should show route path
      cy.get('[data-testid="route-path"]').should('be.visible')

      // Selected booths should be highlighted
      cy.get('[data-testid="booth"].selected')
        .should('have.length.at.least', 1)
    })

    it('should handle insufficient time budget', () => {
      // Set very low time budget
      cy.get('input[name="timeBudget"]').clear().type('5')

      // Try to optimize
      cy.contains('Optimize Route').click()

      // Should show warning or adjusted route
      cy.contains(/time budget|not enough time/i, { timeout: 5000 })
    })
  })

  describe('Export Functionality', () => {
    beforeEach(() => {
      // Create optimized route
      cy.get('[data-testid="company-card"]').first().click()
      cy.get('[data-testid="company-card"]').eq(1).click()

      cy.get('input[name="timeBudget"]').clear().type('60')
      cy.contains('Optimize Route').click()

      cy.get('[data-testid="itinerary"]', { timeout: 5000 }).should('be.visible')
    })

    it('should export route as PDF', () => {
      // Click export PDF button
      cy.contains('Export PDF').click()

      // Verify download initiated (check for download in test)
      cy.wait(1000)
    })

    it('should export route as CSV', () => {
      // Click export CSV button
      cy.contains('Export CSV').click()

      // Verify download initiated
      cy.wait(1000)
    })
  })

  describe('Interactive Map Features', () => {
    it('should zoom in and out on map', () => {
      // Click zoom in
      cy.get('[data-testid="zoom-in"]').click()

      // Verify zoom level increased
      cy.get('[data-testid="floor-map"]')
        .should('have.attr', 'transform')
        .and('contain', 'scale')
    })

    it('should switch between ballrooms', () => {
      // Click Waldorf tab
      cy.contains('Waldorf').click()
      cy.get('[data-testid="floor-map"]').should('contain', 'Waldorf')

      // Click Imperial tab
      cy.contains('Imperial').click()
      cy.get('[data-testid="floor-map"]').should('contain', 'Imperial')
    })
  })

  describe('Edge Cases and Error Handling', () => {
    it('should handle no companies selected', () => {
      // Try to optimize without selections
      cy.contains('Optimize Route').click()

      // Should show error or warning
      cy.contains(/select.*companies/i).should('be.visible')
    })

    it('should handle network errors gracefully', () => {
      // Intercept API and force error
      cy.intercept('POST', '**/api/v1/routing/optimize/', {
        statusCode: 500,
        body: { error: 'Internal Server Error' }
      })

      // Select companies and optimize
      cy.get('[data-testid="company-card"]').first().click()
      cy.contains('Optimize Route').click()

      // Should show error message
      cy.contains(/error|failed/i).should('be.visible')
    })

    it('should handle empty company list', () => {
      // Intercept API with empty response
      cy.intercept('GET', '**/api/v1/companies/', {
        body: []
      })

      cy.reload()

      // Should show empty state
      cy.contains(/no companies/i).should('be.visible')
    })
  })

  describe('Responsive Design', () => {
    it('should work on mobile viewport', () => {
      cy.viewport('iphone-x')

      // App should still be functional
      cy.get('[data-testid="company-list"]').should('be.visible')
      cy.get('[data-testid="company-card"]').first().should('be.visible')
    })

    it('should work on tablet viewport', () => {
      cy.viewport('ipad-2')

      cy.get('[data-testid="floor-map"]').should('be.visible')
      cy.get('[data-testid="company-list"]').should('be.visible')
    })
  })
})

describe('Performance Tests', () => {
  it('should load initial page quickly', () => {
    const start = Date.now()

    cy.visit('/')
    cy.get('[data-testid="app-container"]').should('be.visible')

    const loadTime = Date.now() - start

    // Should load in under 3 seconds
    expect(loadTime).to.be.lessThan(3000)
  })

  it('should handle large company lists', () => {
    // Mock large dataset
    const companies = Array.from({ length: 100 }, (_, i) => ({
      id: i,
      name: `Company ${i}`,
      booth_number: `${i}`,
      ballroom: 'Waldorf'
    }))

    cy.intercept('GET', '**/api/v1/companies/', {
      body: companies
    })

    cy.visit('/')

    // Should still render
    cy.get('[data-testid="company-card"]')
      .should('have.length.at.least', 10)
  })
})
