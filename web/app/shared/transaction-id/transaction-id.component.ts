import {
  AfterViewInit,
  Component,
  Input,
  OnChanges,
  OnInit,
  SimpleChanges
} from '@angular/core';
import { PublicConfigurationService } from '../public.configuration.service';
import { PublicConfiguration } from '../public-configuration.model';

@Component({
  selector: 'app-transaction-id',
  templateUrl: './transaction-id.component.html',
  styleUrls: ['./transaction-id.component.scss']
})
export class TransactionIdComponent
  implements OnInit, OnChanges, AfterViewInit {
  @Input() tx: string;
  @Input() currency: string;

  publicConfiguration: PublicConfiguration;
  href?: string;

  private resetHref() {
    if (this.tx && this.currency && this.publicConfiguration) {
      if (
        this.currency === 'coin' &&
        this.publicConfiguration.coin_transaction_web_link
      ) {
        this.href = this.publicConfiguration.coin_transaction_web_link.replace(
          '{{tx}}',
          this.tx
        );
      } else if (
        this.currency === 'waves' &&
        this.publicConfiguration.waves_transaction_web_link
      ) {
        this.href = this.publicConfiguration.waves_transaction_web_link.replace(
          '{{tx}}',
          this.tx
        );
      } else {
        this.href = null;
      }
    } else {
      this.href = null;
    }
  }

  constructor(publicConfigurationService: PublicConfigurationService) {
    this.publicConfiguration = publicConfigurationService.configuration;
  }

  ngAfterViewInit(): void {
    this.resetHref();
  }

  ngOnChanges(changes: SimpleChanges): void {
    this.resetHref();
  }

  ngOnInit() {
    this.resetHref();
  }
}
