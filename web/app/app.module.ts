import { BrowserModule } from '@angular/platform-browser';
import { APP_INITIALIZER, NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import { RouterModule } from '@angular/router';
import { AttemptListQueryComponent } from './attempt-list-query/atempt-list-query.component';
import { AddressFactoryComponent } from './address-factory/address-factory.component';
import { HttpErrorAlertService } from './shared/http-error-alert.service';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TransactionComponent } from './shared/transaction/transaction.component';
import { PublicConfigurationService } from './shared/public.configuration.service';
import { RestService } from './shared/rest.service';
import { AttemptListComponent } from './attempt-list-query/attempt-list/attempt-list.component';
import { TransactionAddressComponent } from './shared/transaction-address/transaction-address.component';
import { TransactionIdComponent } from './shared/transaction-id/transaction-id.component';
import { PrimaryButtonDirective } from './shared/primary-button.directive';
import { HttpModule } from '@angular/http';
import { ServiceWorkerModule } from '@angular/service-worker';
import { environment } from '../environments/environment';

export function createPublicConfigurationInitializer(
  publicConfigService: PublicConfigurationService
): () => Promise<any> {
  return () => {
    return publicConfigService.init();
  };
}

@NgModule({
  declarations: [
    AppComponent,
    AttemptListQueryComponent,
    AddressFactoryComponent,
    TransactionComponent,
    AttemptListComponent,
    TransactionAddressComponent,
    TransactionIdComponent,
    PrimaryButtonDirective
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    ServiceWorkerModule.register('/static/ngsw-worker.js', {
      enabled: environment.production
    }),
    HttpModule,
    RouterModule.forRoot(
      [
        {
          path: 'address-factory',
          component: AddressFactoryComponent
        },
        {
          path: 'attempt-list-query',
          component: AttemptListQueryComponent
        },
        {
          path: '',
          pathMatch: 'full',
          redirectTo: 'address-factory'
        },
        {
          path: '**',
          redirectTo: 'address-factory'
        }
      ],
      { useHash: true }
    )
  ],
  providers: [
    HttpErrorAlertService,
    PublicConfigurationService,
    RestService,
    {
      provide: APP_INITIALIZER,
      useFactory: createPublicConfigurationInitializer,
      deps: [PublicConfigurationService],
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
