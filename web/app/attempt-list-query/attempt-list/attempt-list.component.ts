import { Component, Input } from '@angular/core';
import { TransactionAttemptList } from '../../shared/attempt-list.model';
import { PublicConfigurationService } from '../../shared/public.configuration.service';
import { PublicConfiguration } from '../../shared/public-configuration.model';

@Component({
  selector: 'app-attempt-list',
  templateUrl: './attempt-list.component.html',
  styleUrls: ['./attempt-list.component.scss']
})
export class AttemptListComponent {
  @Input() attemptList: TransactionAttemptList;

  publicConfiguration: PublicConfiguration;

  constructor(publicConfigurationService: PublicConfigurationService) {
    this.publicConfiguration = publicConfigurationService.configuration;
  }

  isComplete() {
    return (
      this.attemptList.attempts.length === this.attemptList.transactions.length
    );
  }
}
