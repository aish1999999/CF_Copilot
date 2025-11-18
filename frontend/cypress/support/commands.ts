/// <reference types="cypress" />

// Custom commands for CF_Copilot E2E tests

Cypress.Commands.add('getByTestId', (testId: string) => {
  return cy.get(`[data-testid="${testId}"]`)
})

// Command to mock API calls
Cypress.Commands.add('mockCompanies', () => {
  cy.intercept('GET', '**/api/v1/companies/', {
    fixture: 'companies.json'
  }).as('getCompanies')
})

Cypress.Commands.add('mockOptimizeRoute', () => {
  cy.intercept('POST', '**/api/v1/routing/optimize/', {
    fixture: 'optimized_route.json'
  }).as('optimizeRoute')
})

declare global {
  namespace Cypress {
    interface Chainable {
      mockCompanies(): Chainable<void>
      mockOptimizeRoute(): Chainable<void>
    }
  }
}

export {}
